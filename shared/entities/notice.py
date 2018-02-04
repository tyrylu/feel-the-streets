from . import Annotated
from .enums import NoticeImpact,  NoticeFunction, NoticeType, NoticeCategory

class Notice(Annotated):
    category: NoticeCategory = None
    function: NoticeFunction = None
    impact: NoticeImpact = None
    orientation: int = None
    type: NoticeType = None