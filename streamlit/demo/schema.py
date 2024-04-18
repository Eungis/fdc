import streamlit as st
from dataclasses import dataclass
from pydantic import BaseModel
from typing import List, Tuple


class ChatLog(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    question: str
    response: str
    documents: List[dict]


@dataclass
class ChatLogs(object):
    @property
    def session_key(self):
        return "chatlogs"

    @property
    def chatlogs(self) -> List[ChatLog]:
        chatlogs = st.session_state[self.session_key]
        return chatlogs

    def add_chatlog(self, chatlog):
        chatlogs = self.chatlogs
        chatlogs.append(chatlog)

    def if_cached(self, question: str) -> Tuple[bool, ChatLog]:
        chatlogs = self.chatlogs
        result = None
        for chatlog in chatlogs:
            if question in chatlog.question:
                cached = True
                result = chatlog
                break
        else:
            cached = False
        return (cached, result)
