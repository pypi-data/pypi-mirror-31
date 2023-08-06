
# Tag set ids for metadata about media in our system
TAG_SET_PUBLICATION_COUNTRY = 1935  # holds the country of publication of a source
TAG_SET_PUBLICATION_STATE = 1962  # holds the state of publication of a source (only US and India right now)
TAG_SET_PRIMARY_LANGUAGE = 1969  # holds the primary language of a source
TAG_SET_COUNTRY_OF_FOCUS = 1970  # holds the primary focus on what country for a source
TAG_SET_MEDIA_TYPE = 1972  # holds what type of media source this is (broadcast, online, etc)

# Tag set ids for metadata about stories in our system
TAG_SET_DATE_GUESS_METHOD = 508
TAG_SET_EXTRACTOR_VERSION = 1354
TAG_SET_GEOCODER_VERSION = 1937
TAG_SET_NYT_THEMES_VERSION = 1964

'''
These are helpers for calling media/story/sentence tag update methods.  These wrappers exist
because you can specify this by tag/tag-set name, or by tag-id.  Because you don't want to mess
these calls up, I found it helpful to fomarlize this, instead of just accepting a dict from the
caller (which might be missing params).
'''

TAG_ACTION_ADD = 'add'
TAG_ACTION_REMOVE = 'remove'


class TagSpec(object):

    def __init__(self, tag_set_name=None, tag_name=None, action=TAG_ACTION_ADD, tags_id=None):
        self.tag_set_name = tag_set_name
        self.tag_name = tag_name
        self.tags_id = tags_id
        self.action = action

    def isSpecifiedByName(self):
        return (self.tag_name is not None) and (self.tag_set_name is not None)

    def isSpeficiedById(self):
        return self.tags_id is not None

    def getBaseParams(self):
        params = {
            'action': self.action
        }
        if self.isSpeficiedById():
            params['tags_id'] = self.tags_id
        elif self.isSpecifiedByName():
            params['tag'] = self.tag_name
            params['tag_set'] = self.tag_set_name
        return params


class StoryTag(TagSpec):

    def __init__(self, stories_id, tag_set_name=None, tag_name=None, action=TAG_ACTION_ADD, tags_id=None):
        self.stories_id = stories_id
        super(StoryTag, self).__init__(tag_set_name, tag_name, action, tags_id)

    def getParams(self):
        params = { 'stories_id': self.stories_id }
        params.update(self.getBaseParams())
        return params


class SentenceTag(TagSpec):

    def __init__(self, story_sentences_id, tag_set_name=None, tag_name=None, action=TAG_ACTION_ADD, tags_id=None):
        self.story_sentences_id = story_sentences_id
        super(SentenceTag, self).__init__(tag_set_name, tag_name, action, tags_id)

    def getParams(self):
        params = { 'story_sentences_id': self.story_sentences_id }
        params.update(self.getBaseParams())
        return params


class MediaTag(TagSpec):

    def __init__(self, media_id, tag_set_name=None, tag_name=None, action=TAG_ACTION_ADD, tags_id=None):
        self.media_id = media_id
        super(MediaTag, self).__init__(tag_set_name, tag_name, action, tags_id)

    def getParams(self):
        params = { 'media_id': self.media_id }
        params.update(self.getBaseParams())
        return params
