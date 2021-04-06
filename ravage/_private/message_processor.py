from ..core.message_processor import MessageProcessorBase
from ..core.message import Message, MESSAGE_SOURCE_TYPES, MESSAGE_TYPES, ACTIONS

from . import config


class MessageProcessor(MessageProcessorBase):
    def on_message(self, message: Message):
        print(f'Message: {message.source_type.value}:{message.source_id}:{message.type.value}:{message.sub_type}:{message.data}')
        if message.source_type == MESSAGE_SOURCE_TYPES.SOUNDWAVE:
            if message.type == MESSAGE_TYPES.ACTION:
                if message.sub_type == ACTIONS.SHUTDOWN.value:
                    self.send_message(Message(
                        MESSAGE_SOURCE_TYPES.RAVAGE_CORE,
                        MESSAGE_TYPES.ACTION_RESULT,
                        sub_type=ACTIONS.SHUTDOWN.value
                    ))

                else:
                    config.log(f'Unknown ACTION: {message.sub_type}', error=True)

            else:
                config.log(f'Unknown message type: {message.type.value}')

        else:
            config.log(f'Unknown message source type: {message.source_type.value}')

    def on_exception(self, ex: Exception):
        config.log(f'Error while processing message: {ex}')
