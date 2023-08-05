/*! @brief Flag for checking if this header has already been included. */
#ifndef CISZMQCOMM_H_
#define CISZMQCOMM_H_

#include <CommBase.h>

#ifdef ZMQINSTALLED

#include <czmq.h>

static unsigned _zmq_rand_seeded = 0;
static unsigned _last_port_set = 0;
static unsigned _cisSocketsCreated = 0;
static int _last_port = 49152;
/* static double _wait_send_t = 0;  // 0.0001; */
static char _reply_msg[100] = "CIS_REPLY";
static char _purge_msg[100] = "CIS_PURGE";
static int _zmq_sleeptime = 10000;

/*! 
  @brief Struct to store info for reply.
*/
typedef struct zmq_reply_t {
  int nsockets; 
  zsock_t **sockets;
  char **addresses;
  int n_msg;
  int n_rep;
} zmq_reply_t;


// Forward declarations
static inline
int zmq_comm_nmsg(const comm_t x);
static inline
int zmq_comm_recv(const comm_t x, char **data, const size_t len,
		  const int allow_realloc);


/*!
  @brief Free a reply structure.
  @param[in] x zmq_reply_t * Structure to free.
  @returns int 0 if successfull, -1 otherwise.
 */
static inline
int free_zmq_reply(zmq_reply_t *x) {
  int i = 0;
  if (x != NULL) {
    if (x->sockets != NULL) {
      for (i = 0; i < x->nsockets; i++) {
	if (x->sockets[i] != NULL) {
	  zsock_destroy(&(x->sockets[i]));
	  x->sockets[i] = NULL;
	}
      }
      free(x->sockets);
    }
    if (x->addresses != NULL) {
      for (i = 0; i < x->nsockets; i++) {
	if (x->addresses[i] != NULL) {
	  free(x->addresses[i]);
	  x->addresses[i] = NULL;
	}
      }
      free(x->addresses);
    }
    x->nsockets = 0;
  }
  return 0;
}

/*!
  @brief Add empty reply structure information to comm.
  @param[in] comm comm_t * Comm to initialize reply for.
  @returns int 0 if successfull, -1 otherwise.
 */
static inline
int init_zmq_reply(comm_t *comm) {
  zmq_reply_t *zrep = (zmq_reply_t*)malloc(sizeof(zmq_reply_t));
  if (zrep == NULL) {
    cislog_error("init_zmq_reply(%s): Failed to malloc reply.", comm->name);
    return -1;
  }
  zrep->nsockets = 0;
  zrep->sockets = NULL;
  zrep->addresses = NULL;
  zrep->n_msg = 0;
  zrep->n_rep = 0;
  comm->reply = (void*)zrep;
  return 0;
};

/*!
  @brief Locate matching reply socket.
  @param[in] comm comm_t* Comm that should be checked for matching reply socket.
  @param[in] address char* Address that should be matched against.
  @returns int Index of matched socket, -1 if no match, -2 if error.
 */
static inline
int find_reply_socket(const comm_t *comm, const char *address) {
  int ret = -1;
  // Get reply
  zmq_reply_t *zrep = (zmq_reply_t*)(comm->reply);
  if (zrep == NULL) {
    cislog_error("find_reply_socket(%s): Reply structure not initialized.", comm->name);
    return -2;
  }
  int i = 0;
  for (i = 0; i < zrep->nsockets; i++) {
    if (strcmp(zrep->addresses[i], address) == 0) {
      ret = i;
      break;
    }
  }
  return ret;
};

/*!
  @brief Request confirmation from receiving socket.
  @param[in] comm comm_t* Comm structure to do reply for.
  @returns int 0 if successful, -2 on EOF, -1 otherwise.
 */
static inline
int do_reply_send(const comm_t *comm) {
  // Get reply
  zmq_reply_t *zrep = (zmq_reply_t*)(comm->reply);
  if (zrep == NULL) {
    cislog_error("do_reply_send(%s): Reply structure not initialized.", comm->name);
    return -1;
  }
  zrep->n_msg++;
  zsock_t *s = (zsock_t*)(zrep->sockets[0]);
  if (s == NULL) {
    cislog_error("do_reply_send(%s): Socket is NULL.", comm->name);
    return -1;
  }
  // Poll
  cislog_debug("do_reply_send(%s): address=%s, begin", comm->name,
  	       zrep->addresses[0]);
  zpoller_t *poller = zpoller_new(s, NULL);
  if (poller == NULL) {
    cislog_error("do_reply_send(%s): Could not create poller", comm->name);
    return -1;
  }
  void *p = zpoller_wait(poller, -1);
  zpoller_destroy(&poller);
  if (p == NULL) {
    if (zpoller_terminated(poller)) {
      cislog_error("do_reply_send(%s): Poller interrupted", comm->name);
    } else if (zpoller_expired(poller)) {
      cislog_error("do_reply_send(%s): Poller expired", comm->name);
    } else {
      cislog_error("do_reply_send(%s): Poller failed", comm->name);
    }
    return -1;
  }
  // Receive
  zframe_t *msg = zframe_recv(s);
  if (msg == NULL) {
    cislog_error("do_reply_send(%s): did not receive", comm->name);
    return -1;
  }
  char *msg_data = (char*)zframe_data(msg);
  // Check for EOF
  int is_purge = 0;
  if (strcmp(msg_data, CIS_MSG_EOF) == 0) {
    cislog_debug("do_reply_send(%s): EOF received", comm->name);
    zrep->n_msg = 0;
    zrep->n_rep = 0;
    return -2;
  } else if (strcmp(msg_data, _purge_msg) == 0) {
    is_purge = 1;
  }
  // Send
  // zsock_set_linger(s, _zmq_sleeptime);
  int ret = zframe_send(&msg, s, 0);
  // Check for purge or EOF
  if (ret < 0) {
    cislog_error("do_reply_send(%s): Error sending reply frame.", comm->name);
    zframe_destroy(&msg);
  } else {
    if (is_purge == 1) {
      cislog_debug("do_reply_send(%s): PURGE received", comm->name);
      zrep->n_msg = 0;
      zrep->n_rep = 0;
      ret = do_reply_send(comm);
    } else {
      zrep->n_rep++;
    }
  }
  cislog_debug("do_reply_send(%s): address=%s, end", comm->name,
	       zrep->addresses[0]);
  return ret;
};

/*!
  @brief Send confirmation to sending socket.
  @param[in] comm comm_t* Comm structure to do reply for.
  @param[in] isock int Index of socket that reply should be done for.
  @param[in] msg char* Mesage to send/recv.
  @returns int 0 if successfule, -1 otherwise.
 */
static inline
int do_reply_recv(const comm_t *comm, const int isock, const char *msg) {
  // Get reply
  zmq_reply_t *zrep = (zmq_reply_t*)(comm->reply);
  if (zrep == NULL) {
    cislog_error("do_reply_recv(%s): Reply structure not initialized.", comm->name);
    return -1;
  }
  zsock_t *s = (zsock_t*)(zrep->sockets[isock]);
  if (s == NULL) {
    cislog_error("do_reply_recv(%s): Socket is NULL.", comm->name);
    return -1;
  }
  cislog_debug("do_reply_recv(%s): address=%s, begin", comm->name,
	       zrep->addresses[isock]);
  zframe_t *msg_send = zframe_new(msg, strlen(msg));
  if (msg_send == NULL) {
    cislog_error("do_reply_recv(%s): Error creating frame.", comm->name);
    return -1;
  }
  // Send
  int ret = zframe_send(&msg_send, s, 0);
  if (ret < 0) {
    cislog_error("do_reply_recv(%s): Error sending confirmation.", comm->name);
    zframe_destroy(&msg_send);
    return -1;
  }
  if (strcmp(msg, CIS_MSG_EOF) == 0) {
    zrep->n_msg = 0;
    zrep->n_rep = 0;
    zsock_set_linger(s, _zmq_sleeptime);
    return -2;
  }
  // Receive
  zframe_t *msg_recv = zframe_recv(s);
  if (msg_recv == NULL) {
    cislog_error("do_reply_recv(%s): did not receive", comm->name);
    return -1;
  }
  zframe_destroy(&msg_recv);
  zrep->n_rep++;
  cislog_debug("do_reply_recv(%s): address=%s, end", comm->name,
	       zrep->addresses[isock]);
  return 0;
};

/*!
  @brief Add information about reply socket to outgoing message.
  @param[in] comm comm_t* Comm that confirmation is for.
  @param[in] data char* Message that reply info should be added to.
  @param[in] len int Length of the outgoing message.
  @returns char* Message with reply information added.
 */
static inline
char* check_reply_send(const comm_t *comm, const char *data, const int len,
		       int *new_len) {
  char *out = NULL;
  new_len[0] = len;
  // Get reply
  zmq_reply_t *zrep = (zmq_reply_t*)(comm->reply);
  if (zrep == NULL) {
    cislog_error("check_reply_send(%s): Reply structure not initialized.", comm->name);
    return out;
  }
  // Create socket
  if (zrep->nsockets == 0) {
    zrep->sockets = (zsock_t**)malloc(sizeof(zsock_t*));
    if (zrep->sockets == NULL) {
      cislog_error("check_reply_send(%s): Error mallocing sockets.", comm->name);
      return out;
    }
    zrep->nsockets = 1;
    zrep->sockets[0] = zsock_new(ZMQ_REP);
    zsock_set_linger(zrep->sockets[0], 0);
    if (zrep->sockets[0] == NULL) {
      cislog_error("check_reply_send(%s): Could not initialize empty socket.",
		   comm->name);
      return out;
    }
    char protocol[50] = "tcp";
    char host[50] = "localhost";
    if (strcmp(host, "localhost") == 0)
      strcpy(host, "127.0.0.1");
    char address[100];
    if (_last_port_set == 0) {
      cislog_debug("model_index = %s", getenv("CIS_MODEL_INDEX"));
      _last_port = 49152 + 1000 * atoi(getenv("CIS_MODEL_INDEX"));
      _last_port_set = 1;
      cislog_debug("_last_port = %d", _last_port);
    }
    sprintf(address, "%s://%s:*[%d-]", protocol, host, _last_port + 1);
    int port = zsock_bind(zrep->sockets[0], "%s", address);
    if (port == -1) {
      cislog_error("check_reply_send(%s): Could not bind socket to address = %s",
		   comm->name, address);
      return out;
    }
    _last_port = port;
    sprintf(address, "%s://%s:%d", protocol, host, port);
    zrep->addresses = (char**)malloc(sizeof(char*));
    zrep->addresses[0] = (char*)malloc((strlen(address) + 1)*sizeof(char));
    strcpy(zrep->addresses[0], address);
  }
  // Add address to new message
  out = (char*)malloc(2*(strlen(_reply_msg) + 2) +
		      strlen(zrep->addresses[0]) + len + 1);
  sprintf(out, ":%s:%s:%s:", _reply_msg, zrep->addresses[0], _reply_msg);
  new_len[0] = len + (int)strlen(out);
  memcpy(out + strlen(out), data, len);
  out[new_len[0]] = '\0';
  return out;
};


/*!
  @brief Get reply information from message.
  @param[in] comm comm_* Comm structure for incoming message.
  @param[in, out] data char* Received message containing reply info that will be
  removed on return.
  @param[in] len size_t Length of received message.
  @returns int Length of message without the reply info. -1 if there is an error.
 */
static inline
int check_reply_recv(const comm_t *comm, char *data, const size_t len) {
  int new_len = (int)len;
  int ret = 0;
  // Get reply
  zmq_reply_t *zrep = (zmq_reply_t*)(comm->reply);
  if (zrep == NULL) {
    cislog_error("check_reply_recv(%s): Reply structure not initialized.", comm->name);
    return -1;
  }
  zrep->n_msg++;
  // Extract address
  char re_reply[500];
  sprintf(re_reply, ":%s:(.*):%s:", _reply_msg, _reply_msg);
  size_t sind, eind;
  ret = find_match(re_reply, data, &sind, &eind);
  if (ret <= 0) {
    cislog_error("check_reply_recv(%s): Error parsing reply header in '%s'",
		 comm->name, data);
    return -1;
  }
  size_t headsiz = (eind-sind);
  new_len = (int)(len - headsiz);
  char address[100];
  headsiz -= (2*(strlen(_reply_msg) + 2));
  memcpy(address, data + sind + strlen(_reply_msg) + 2, headsiz);
  address[headsiz] = '\0';
  memmove(data, data + eind, new_len);
  data[new_len] = '\0';
  // Match address and create if it dosn't exist
  int isock = find_reply_socket(comm, address);
  if (isock < 0) {
    if (isock == -2) {
      cislog_error("check_reply_recv(%s): Error locating socket.", comm->name);
      return -1;
    }
    // Realloc arrays
    zrep->sockets = (zsock_t**)realloc(zrep->sockets,
				       sizeof(zsock_t*)*(zrep->nsockets + 1));
    if (zrep->sockets == NULL) {
      cislog_error("check_reply_recv(%s): Error reallocing sockets.", comm->name);
      return -1;
    }
    zrep->addresses = (char**)realloc(zrep->addresses,
				      sizeof(char*)*(zrep->nsockets + 1));
    if (zrep->addresses == NULL) {
      cislog_error("check_reply_recv(%s): Error reallocing addresses.", comm->name);
      return -1;
    }
    // Create new socket
    isock = zrep->nsockets;
    zrep->nsockets++;
    zrep->sockets[isock] = zsock_new(ZMQ_REQ);
    zsock_set_linger(zrep->sockets[isock], 0);
    if (zrep->sockets[isock] == NULL) {
      cislog_error("check_reply_recv(%s): Could not initialize empty socket.",
		   comm->name);
      return -1;
    }
    zrep->addresses[isock] = (char*)malloc(sizeof(char)*(strlen(address) + 1));
    if (zrep->addresses[isock] == NULL) {
      cislog_error("check_reply_recv(%s): Could not realloc new address.",
		   comm->name);
      return -1;
    }
    strcpy(zrep->addresses[isock], address);
    ret = zsock_connect(zrep->sockets[isock], "%s", address);
    if (ret < 0) {
      cislog_error("check_reply_recv(%s): Could not connect to socket.",
		   comm->name);
      return -1;
    }
  }
  // Confirm message receipt
  ret = do_reply_recv(comm, isock, _reply_msg);
  if (ret < 0) {
    cislog_error("check_reply_recv(%s): Error during reply.", comm->name);
    return -1;
  }
  return new_len;
};

/*!
  @brief Create a new socket.
  @param[in] comm comm_t * Comm structure initialized with new_comm_base.
  @returns int -1 if the address could not be created.
*/
static inline
int new_zmq_address(comm_t *comm) {
  // TODO: Get protocol/host from input
  char protocol[50] = "tcp";
  char host[50] = "localhost";
  char address[100];
  if (strcmp(host, "localhost") == 0)
    strcpy(host, "127.0.0.1");
  if ((strcmp(protocol, "inproc") == 0) ||
      (strcmp(protocol, "ipc") == 0)) {
    // TODO: small chance of reusing same number
    int key = 0;
    if (!(_zmq_rand_seeded)) {
      srand(ptr2seed(comm));
      _zmq_rand_seeded = 1;
    }
    while (key == 0) key = rand();
    if (strlen(comm->name) == 0)
      sprintf(comm->name, "tempnewZMQ-%d", key);
    sprintf(address, "%s://%s", protocol, comm->name);
  } else {
     if (_last_port_set == 0) {
      cislog_debug("model_index = %s", getenv("CIS_MODEL_INDEX"));
      _last_port = 49152 + 1000 * atoi(getenv("CIS_MODEL_INDEX"));
      _last_port_set = 1;
      cislog_debug("_last_port = %d", _last_port);
    }
   sprintf(address, "%s://%s:*[%d-]", protocol, host, _last_port + 1);
    /* strcat(address, ":!"); // For random port */
  }
  // Bind
  zsock_t *s = zsock_new(ZMQ_PAIR);
  if (s == NULL) {
    cislog_error("new_zmq_address: Could not initialize empty socket.");
    return -1;
  }
  zsock_set_linger(s, 0);
  int port = zsock_bind(s, "%s", address);
  if (port == -1) {
    cislog_error("new_zmq_address: Could not bind socket to address = %s",
		 address);
    return -1;
  }
  // Add port to address
  if ((strcmp(protocol, "inproc") != 0) &&
      (strcmp(protocol, "ipc") != 0)) {
    _last_port = port;
    sprintf(address, "%s://%s:%d", protocol, host, port);
  }
  strcpy(comm->address, address);
  cislog_debug("new_zmq_address: Bound socket to %s", comm->address);
  if (strlen(comm->name) == 0)
    sprintf(comm->name, "tempnewZMQ-%d", port);
  comm->handle = (void*)s;
  _cisSocketsCreated++;
  // Init reply
  int ret = init_zmq_reply(comm);
  return ret;
};

/*!
  @brief Initialize a ZeroMQ communicator.
  @param[in] comm comm_t * Comm structure initialized with init_comm_base.
  @returns int -1 if the comm could not be initialized.
 */
static inline
int init_zmq_comm(comm_t *comm) {
  int ret = -1;
  if (comm->valid == 0)
    return ret;
  zsock_t *s = zsock_new(ZMQ_PAIR);
  if (s == NULL) {
    cislog_error("init_zmq_address: Could not initialize empty socket.");
    return -1;
  }
  zsock_set_linger(s, 0);
  ret = zsock_connect(s, "%s", comm->address);
  if (ret == -1) {
    cislog_error("init_zmq_address: Could not connect socket to address = %s",
  		 comm->address);
    zsock_destroy(&s);
    return ret;
  }
  cislog_debug("init_zmq_address: Connected socket to %s", comm->address);
  if (strlen(comm->name) == 0)
    sprintf(comm->name, "tempinitZMQ-%s", comm->address);
  // Asign to void pointer
  comm->handle = (void*)s;
  ret = init_zmq_reply(comm);
  return ret;
};

/*!
  @brief Perform deallocation for ZMQ communicator.
  @param[in] x comm_t Pointer to communicator to deallocate.
  @returns int 1 if there is and error, 0 otherwise.
*/
static inline
int free_zmq_comm(comm_t *x) {
  int ret = 0;
  if (x == NULL)
    return ret;
  // Drain input
  if ((is_recv(x->direction)) && (x->valid == 1)) {
    if (_cis_error_flag == 0) {
      size_t data_len = 100;
      char *data = (char*)malloc(data_len);
      while (zmq_comm_nmsg(*x) > 0) {
        ret = zmq_comm_recv(*x, &data, data_len, 1);
        if (ret < 0) {
          if (ret == -2) {
            x->recv_eof[0] = 1;
            break;
          }
        }
      }
      free(data);
    }
  }
  // Free reply
  if (x->reply != NULL) {
    zmq_reply_t *zrep = (zmq_reply_t*)(x->reply);
    // Free reply
    ret = free_zmq_reply(zrep);
    free(x->reply);
    x->reply = NULL;
  }
  if (x->handle != NULL) {
    zsock_t *s = (zsock_t*)(x->handle);
    if (s != NULL) {
      cislog_debug("Destroying socket: %s", x->address);
      zsock_destroy(&s);
    }
    x->handle = NULL;
  }
  return ret;
};

/*!
  @brief Get number of messages in the comm.
  @param[in] comm_t Communicator to check.
  @returns int Number of messages. -1 indicates an error.
 */
static inline
int zmq_comm_nmsg(const comm_t x) {
  int out = 0;
  if (is_recv(x.direction)) {
    if (x.handle != NULL) {
      zsock_t *s = (zsock_t*)(x.handle);
      zpoller_t *poller = zpoller_new(s, NULL);
      if (poller == NULL) {
	cislog_error("zmq_comm_nmsg: Could not create poller");
	return -1;
      }
      void *p = zpoller_wait(poller, 1);
      if (p == NULL) {
	if (zpoller_terminated(poller)) {
	  cislog_error("zmq_comm_nmsg: Poller interrupted");
	  out = -1;
	} else {
	  out = 0;
	}
      } else {
	out = 1;
      }
      zpoller_destroy(&poller);
    }
  } else {
    /* if (x.last_send[0] != 0) { */
    /*   time_t now; */
    /*   time(&now); */
    /*   double elapsed = difftime(now, x.last_send[0]); */
    /*   if (elapsed > _wait_send_t) */
    /* 	out = 0; */
    /*   else */
    /* 	out = 1; */
    /* } */
    zmq_reply_t *zrep = (zmq_reply_t*)(x.reply);
    if (zrep != NULL) {
      cislog_debug("zmq_comm_nmsg(%s): nmsg = %d, nrep = %d",
		   x.name, zrep->n_msg, zrep->n_rep);
      out = zrep->n_msg - zrep->n_rep;
    }
  }
  return out;
};

/*!
  @brief Send a message to the comm.
  Send a message smaller than CIS_MSG_MAX bytes to an output comm. If the
  message is larger, it will not be sent.
  @param[in] x comm_t structure that comm should be sent to.
  @param[in] data character pointer to message that should be sent.
  @param[in] len size_t length of message to be sent.
  @returns int 0 if send succesfull, -1 if send unsuccessful.
 */
static inline
int zmq_comm_send(const comm_t x, const char *data, const size_t len) {
  cislog_debug("zmq_comm_send(%s): %d bytes", x.name, len);
  if (comm_base_send(x, data, len) == -1)
    return -1;
  zsock_t *s = (zsock_t*)(x.handle);
  if (s == NULL) {
    cislog_error("zmq_comm_send(%s): socket handle is NULL", x.name);
    return -1;
  }
  int new_len = 0;
  char *new_data = check_reply_send(&x, data, (int)len, &new_len);
  if (new_data == NULL) {
    cislog_error("zmq_comm_send(%s): Adding reply address failed.", x.name);
    return -1;
  }
  zframe_t *f = zframe_new(new_data, new_len);
  int ret = -1;
  if (f == NULL) {
    cislog_error("zmq_comm_send(%s): frame handle is NULL", x.name);
  } else {
    ret = zframe_send(&f, s, 0);
    if (ret < 0) {
      cislog_error("zmq_comm_send(%s): Error in zframe_send", x.name);
      zframe_destroy(&f);
    }
  }
  // Get reply
  if (ret >= 0) {
    ret = do_reply_send(&x);
    if (ret < 0) {
      if (ret == -2) {
	cislog_error("zmq_comm_send(%s): EOF received", x.name);
      } else {
	cislog_error("zmq_comm_send(%s): Error in do_reply_send", x.name);
      }
    }
  }
  cislog_debug("zmq_comm_send(%s): returning %d", x.name, ret);
  free(new_data);
  return ret;
};

/*!
  @brief Receive a message from an input comm.
  Receive a message smaller than CIS_MSG_MAX bytes from an input comm.
  @param[in] x comm_t structure that message should be sent to.
  @param[out] data char ** pointer to allocated buffer where the message
  should be saved. This should be a malloc'd buffer if allow_realloc is 1.
  @param[in] len const size_t length of the allocated message buffer in bytes.
  @param[in] allow_realloc const int If 1, the buffer will be realloced if it
  is not large enought. Otherwise an error will be returned.
  @returns int -1 if message could not be received. Length of the received
  message if message was received.
 */
static inline
int zmq_comm_recv(const comm_t x, char **data, const size_t len,
		  const int allow_realloc) {
  cislog_debug("zmq_comm_recv(%s)", x.name);
  zsock_t *s = (zsock_t*)(x.handle);
  if (s == NULL) {
    cislog_error("zmq_comm_recv(%s): socket handle is NULL", x.name);
    return -1;
  }
  while (1) {
    int nmsg = zmq_comm_nmsg(x);
    if (nmsg < 0) return -1;
    else if (nmsg > 0) break;
    else {
      cislog_debug("zmq_comm_recv(%s): no messages, sleep", x.name);
      usleep(CIS_SLEEP_TIME);
    }
  }
  zframe_t *out = zframe_recv(s);
  if (out == NULL) {
    cislog_debug("zmq_comm_recv(%s): did not receive", x.name);
    return -1;
  }
  size_t len_recv = zframe_size(out) + 1;
  if (len_recv > len) {
    if (allow_realloc) {
      cislog_debug("zmq_comm_recv(%s): reallocating buffer from %d to %d bytes.",
		   x.name, len, len_recv);
      (*data) = (char*)realloc(*data, len_recv);
      if (*data == NULL) {
	cislog_error("zmq_comm_recv(%s): failed to realloc buffer.", x.name);
	zframe_destroy(&out);
	return -1;
      }
    } else {
      cislog_error("zmq_comm_recv(%s): buffer (%d bytes) is not large enough for message (%d bytes)",
		   x.name, len, len_recv);
      zframe_destroy(&out);
      return -((int)(len_recv - 1));
    }
  }
  memcpy(*data, zframe_data(out), len_recv);
  (*data)[len_recv-1] = '\0';
  zframe_destroy(&out);
  int ret = (int)len_recv - 1;
  ret = check_reply_recv(&x, *data, (size_t)ret);
  cislog_debug("zmq_comm_recv(%s): returning %d", x.name, ret);
  return ret;
};


// Definitions in the case where ZMQ libraries not installed
#else /*ZMQINSTALLED*/

/*!
  @brief Print error message about ZMQ library not being installed.
 */
static inline
void zmq_install_error() {
  cislog_error("Compiler flag 'ZMQINSTALLED' not defined so ZMQ bindings are disabled.");
};

/*!
  @brief Perform deallocation for ZMQ communicator.
  @param[in] x comm_t Pointer to communicator to deallocate.
  @returns int 1 if there is and error, 0 otherwise.
*/
static inline
int free_zmq_comm(comm_t *x) {
  zmq_install_error();
  return 1;
};

/*!
  @brief Create a new socket.
  @param[in] comm comm_t * Comm structure initialized with new_comm_base.
  @returns int -1 if the address could not be created.
*/
static inline
int new_zmq_address(comm_t *comm) {
  zmq_install_error();
  return -1;
};

/*!
  @brief Initialize a ZeroMQ communicator.
  @param[in] comm comm_t * Comm structure initialized with init_comm_base.
  @returns int -1 if the comm could not be initialized.
 */
static inline
int init_zmq_comm(comm_t *comm) {
  zmq_install_error();
  return -1;
};

/*!
  @brief Get number of messages in the comm.
  @param[in] x comm_t Communicator to check.
  @returns int Number of messages. -1 indicates an error.
 */
static inline
int zmq_comm_nmsg(const comm_t x) {
  zmq_install_error();
  return -1;
};

/*!
  @brief Send a message to the comm.
  Send a message smaller than CIS_MSG_MAX bytes to an output comm. If the
  message is larger, it will not be sent.
  @param[in] x comm_t structure that comm should be sent to.
  @param[in] data character pointer to message that should be sent.
  @param[in] len size_t length of message to be sent.
  @returns int 0 if send succesfull, -1 if send unsuccessful.
 */
static inline
int zmq_comm_send(const comm_t x, const char *data, const size_t len) {
  zmq_install_error();
  return -1;
};

/*!
  @brief Receive a message from an input comm.
  Receive a message smaller than CIS_MSG_MAX bytes from an input comm.
  @param[in] x comm_t structure that message should be sent to.
  @param[out] data char ** pointer to allocated buffer where the message
  should be saved. This should be a malloc'd buffer if allow_realloc is 1.
  @param[in] len const size_t length of the allocated message buffer in bytes.
  @param[in] allow_realloc const int If 1, the buffer will be realloced if it
  is not large enought. Otherwise an error will be returned.
  @returns int -1 if message could not be received. Length of the received
  message if message was received.
 */
static inline
int zmq_comm_recv(const comm_t x, char **data, const size_t len,
		  const int allow_realloc) {
  zmq_install_error();
  return -1;
};

#endif /*ZMQINSTALLED*/
#endif /*CISZMQCOMM_H_*/
