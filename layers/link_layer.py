from layers.layer_base import LayerBase, BaseLayerArgs
from queue import Queue

class LinkLayerArgs(BaseLayerArgs):
    pass

class LinkLayer(LayerBase):
    def process_send(self, msg):
        self.receive_buffer.put(msg)