from layers.layer_base import LayerBase, BaseLayerArgs
from queue import Queue
import packet
import time
from threading import Thread

class TransportLayerArgs(BaseLayerArgs):
    pass

class TransportLayer(LayerBase):
    def __init__(self, node_data, layer_id, args):
        super(TransportLayer, self).__init__(node_data, layer_id, args)
        self.ack_buffer = []
        self.current_seq = 0
        self.wait_time = 1

    def process_send(self, msg):
        if msg.transport.type_id == 0 and msg.transport.tcp_type == 0:
            # When sending a TCP seq packet
            msg.transport.seq_num = self.current_seq
            self.current_seq += 1
            msg.network = packet.NetworkingPacket(self.node_data.id, msg.app.dest_id)
            retransmit_thread = Thread(target=self.retransmit, args=(msg, self.wait_time))
            retransmit_thread.daemon = True
            retransmit_thread.start()
            self.ack_buffer.append(msg)  # might need to use copy constructor
        self.below_layer.send_buffer.put(msg)

    def process_receive(self, msg):
        if msg.transport.type_id == 0:
            # On TCP packet received
            if msg.transport.tcp_type == 1:
                # On ack received
                acked_message = next((seq_pckt for seq_pckt in self.ack_buffer if seq_pckt.transport.seq_num == msg.transport.ack_num), None)
                if acked_message is not None:
                    self.ack_buffer.remove(acked_message)
                    #print("Ack (id=%d) found for %s" % (self.node_data.id, acked_message))
            else:
                # On packet received
                pckt = packet.Packet()
                pckt.transport = packet.TransportPacket(0, 1, 0, msg.transport.seq_num)
                pckt.network = packet.NetworkingPacket(self.node_data.id, msg.network.src_id)
                self.send_buffer.put(pckt)
                self.above_layer.receive_buffer.put(msg)
        else:
            # On UDP packet received
            self.above_layer.receive_buffer.put(msg)

    def retransmit(self, msg, wait_time):
        time.sleep(wait_time)
        if msg in self.ack_buffer:
            retransmit_thread = Thread(target=self.retransmit, args=(msg, wait_time))
            retransmit_thread.daemon = True
            retransmit_thread.start()
            self.below_layer.send_buffer.put(msg)


