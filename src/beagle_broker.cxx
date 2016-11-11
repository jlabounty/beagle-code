/* Determines whether master or slave based on IP address, then runs zmq message
broker accepts requests from the outside and makes sure they
get to the appropriate worker and then back where they came from
the "master" is in charge of the BK controls
and will route messages to the other beagle bone
right now master is 192.168.x.21
       and slave is 192.168.x.22

Aaron Fienberg
October 2016
*/

#include <iostream>
#include <memory>
#include <map>
#include <vector>
#include <string>
#include <stdexcept>
#include <cstdio>
#include <cassert>

#include <zmq.hpp>
#include <zmq_addon.hpp>  // for multimessage

// find ip address of the beagle bone
// returns as vector of unsigned ints,
// i.e. x.x.x.x becomes {x, x, x, x}
std::vector<unsigned int> getip();

// peel one word off the string, starting at startiter
// assumes words are separated by delimiter
// returns empty string if no word could be peeled off
// upon return, startiter is at location following the delimeter after the word
// that was found, or end if it is the last word
std::string peel_word(const std::string& str,
                      std::string::const_iterator& startiter,
                      char delimiter = ' ');

typedef struct {
  zmq::socket_t sock;
  short* reventsp;
} pollsock;

int main() {
  auto ipaddr = getip();
  bool is_master = false;
  if (ipaddr.back() == 21) {
    is_master = true;
    std::cout << "is master!" << std::endl;
  } else if (ipaddr.back() != 22) {
    std::string ipstr;
    for (unsigned int i = 0; i < ipaddr.size() - 1; ++i) {
      ipstr += std::to_string(ipaddr[i]) + ".";
    }
    ipstr += std::to_string(ipaddr.back());

    std::cerr << "invalid ip address: " << ipstr << std::endl;
    std::cerr << "should be 192.168.(x).21 or 192.168.(x).22" << std::endl;
  }

  // start broker sockets and prepare pollitems
  zmq::context_t ctxt(1);
  std::vector<zmq::pollitem_t> pollitems;
  zmq::socket_t router(ctxt, ZMQ_ROUTER);
  router.bind("tcp://*:6669");
  pollitems.push_back({(void*)router, 0, ZMQ_POLLIN, 0});

  std::vector<std::string> dealerSockNames = {"spi1", "spi2"};
  if (is_master) {
    dealerSockNames.push_back("bk1");
    dealerSockNames.push_back("bk2");
    dealerSockNames.push_back("bk3");
    dealerSockNames.push_back("bk4");
    dealerSockNames.push_back("slave");
  } else {
    dealerSockNames.push_back("filter");
  }

  // prepare all dealer sockets
  // important to reserve dealer pollitems in advance
  // or reventsp will not work correctly
  pollitems.reserve(1 + dealerSockNames.size());
  std::map<std::string, std::shared_ptr<pollsock>> dealers;
  for (const auto& newName : dealerSockNames) {
    zmq::socket_t newDealer(ctxt, ZMQ_DEALER);
    std::string addrstr;
    if (newName == "slave") {
      addrstr += "tcp://192.168.";
      addrstr += std::to_string(ipaddr[2]) + ".22:6669";
    } else {
      addrstr = "ipc://" + newName + ".ipc";
    }
    newDealer.connect(addrstr);

    std::cout << addrstr << std::endl;

    pollitems.push_back({(void*)newDealer, 0, ZMQ_POLLIN, 0});
    auto newPair = std::make_pair(
        newName, std::make_shared<pollsock>(pollsock{
                     std::move(newDealer), &(pollitems.back().revents)}));
    dealers.insert(std::move(newPair));
  }

  // start polling
  while (true) {
    std::cout << "polling" << std::endl;
    zmq::poll(pollitems.data(), pollitems.size(), -1);

    // check if there's a message on the router
    if (pollitems[0].revents & ZMQ_POLLIN) {
      std::cout << "router message!" << std::endl;
      // we have a message on router,
      // grab message
      zmq::multipart_t mmsg(router);

      // peel words off message to figure out where it goes
      auto lastmsg = mmsg.remove();
      std::string msgstr(lastmsg.data<char>(), lastmsg.size());
      auto striter = msgstr.cbegin();
      auto first_word = peel_word(msgstr, striter);
      auto past_first_iter = striter;
      auto second_word = peel_word(msgstr, striter);

      // determine correct dealer name based on first and second words
      std::string dealername;
      zmq::message_t dealermsg;
      if (first_word == "board") {
        // board refers to breakout board, indicates spi interface command
        int board_num = atoi(second_word.c_str());
        if (board_num > 2) {
          dealername = "slave";
          // send to slave and reduce board_num by 2
          auto reduced_num = std::to_string(board_num - 2);
          std::string dealermsgstr = first_word + " " + reduced_num + " " +
                                     std::string(striter, msgstr.cend());
          dealermsg = zmq::message_t(dealermsgstr.begin(), dealermsgstr.end());
        } else {
          dealername = "spi" + second_word;
          dealermsg = zmq::message_t(striter, msgstr.cend());
        }
      } else if (first_word == "bk") {
        dealername = "bk" + second_word;
        dealermsg = zmq::message_t(striter, msgstr.cend());
      } else if (first_word == "filter") {
        if (is_master) {
          dealername = "slave";
          dealermsg = std::move(lastmsg);
        } else {
          dealername = "filter";
          dealermsg = zmq::message_t(past_first_iter, msgstr.cend());
        }
      }

      // done figuring, send message through appropriate dealer socket
      // or if it doesn't exist, send back "unrecognized msg"
      auto dealeriter = dealers.find(dealername);
      if (dealeriter != dealers.end()) {
        std::cout << "dealer name: " << dealername << std::endl;
        std::cout << "dealer msg: "
                  << std::string(dealermsg.data<char>(), dealermsg.size())
                  << std::endl;
        mmsg.add(std::move(dealermsg));
        mmsg.send(dealeriter->second->sock);
      } else {
        std::cout << "dealer msg: "
                  << std::string(dealermsg.data<char>(), dealermsg.size())
                  << std::endl;
        mmsg.addstr("unrecognized msg");
        mmsg.send(router);
      }
    } else {
      // search all dealers for messages
      for (auto& psockpair : dealers) {
        if (*(psockpair.second->reventsp) & ZMQ_POLLIN) {
          std::cout << "message ready on " << psockpair.first << std::endl;
          // just send it straight through the router
          zmq::multipart_t(psockpair.second->sock).send(router);
        }
      }
    }
  }
}

// subprocess code taken from
// http://stackoverflow.com/questions/478898/how-to-execute-a-command-and-get-output-of-command-within-c-using-posix
// top answer
std::vector<unsigned int> getip() {
  char buffer[128];
  std::string ipstr;
  std::shared_ptr<FILE> pipe(popen("./getIp.sh", "r"), pclose);
  if (!pipe) {
    throw std::runtime_error("popen() failed!");
  }
  while (!feof(pipe.get())) {
    if (fgets(buffer, 128, pipe.get()) != NULL) {
      ipstr += buffer;
    }
  }

  std::vector<unsigned int> out;
  auto iter = ipstr.cbegin();
  while (iter != ipstr.cend()) {
    auto numstr = peel_word(ipstr, iter, '.');
    out.push_back(atoi(numstr.c_str()));
  }

  if (out.size() != 4) {
    throw std::runtime_error("getIp.sh returned invalid ip address!");
  }
  return out;
}

std::string peel_word(const std::string& str,
                      std::string::const_iterator& startiter, char delimiter) {
  auto deliter = std::find(startiter, str.end(), delimiter);
  std::string word;
  if (startiter < str.end()) {
    word = {startiter, deliter};
  }
  if (deliter != str.end()) {
    ++deliter;
  }
  startiter = deliter;
  return word;
}
