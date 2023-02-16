import dateutil
from html import unescape

from Acquisition import aq_base
from BTrees.LLBTree import LLSet

from zope.annotation.interfaces import IAnnotations

from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.comment import Comment

DISCUSSION_ANNOTATION_KEY = "plone.app.discussion:conversation"
## importer.logger.warning(

def task(importer, container, data):
    """ """
    obj_id = data['id']

    if not obj_id in container.objectIds():
        return

    obj = container[obj_id]

    if len(data['conversation']['items']) == 0:
        importer.logger.info(f"No comments for { '/'.join(obj.getPhysicalPath()) }")
        return

    # ...
    added = 0
    conversation = IConversation(obj)

    for item in data['conversation']['items']:

        comment = Comment()

        comment_id = int(item["comment_id"])
        comment.comment_id = comment_id

        comment.creation_date = dateutil.parser.parse(item["creation_date"])
        comment.modification_date = dateutil.parser.parse(
            item["modification_date"]
        )

        comment.author_name = item["author_name"]
        comment.author_username = item["author_username"]
        comment.creator = item["author_username"]

        comment.text = unescape(
            item["text"]
            .replace(u"\r<br />", u"\r\n")
            .replace(u"<br />", u"\r\n")
        )

        if item["user_notification"]:
            comment.user_notification = True

        if item.get("in_reply_to"):
            comment.in_reply_to = int(item["in_reply_to"])

        conversation._comments[comment_id] = comment

        comment.__parent__ = aq_base(conversation)

        commentator = comment.author_username
        if commentator:
            if commentator not in conversation._commentators:
                conversation._commentators[commentator] = 0
            conversation._commentators[commentator] += 1

        reply_to = comment.in_reply_to
        if not reply_to:
            # top level comments are in reply to the faux id 0
            comment.in_reply_to = reply_to = 0

        if reply_to not in conversation._children:
            conversation._children[reply_to] = LLSet()
        conversation._children[reply_to].insert(comment_id)

        # Add the annotation if not already done
        annotions = IAnnotations(obj)
        if DISCUSSION_ANNOTATION_KEY not in annotions:
            annotions[DISCUSSION_ANNOTATION_KEY] = aq_base(conversation)

        added += 1

    importer.logger.info(f"Added #{added} comments to { '/'.join(obj.getPhysicalPath()) }")
