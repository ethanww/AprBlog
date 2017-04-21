from . import db
from flask import Markup
'''导入支持markdown文本内容的相关库'''
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from datetime import datetime
from . import admin
from flask_admin.contrib.mongoengine import ModelView
from flask_wtf import Form

oembed_providers = bootstrap_basic(OEmbedCache())

'''数据库模型，采用MongoDB'''
class Post(db.Document):
    title=db.StringField(max_length=80,required=True)
    content=db.StringField()
    timestamp=db.DateTimeField(default=datetime.utcnow)
    published=db.BooleanField(default=False)
    # category_id=db.
    # category=db.ReferenceField('Category')
    # category=db.ListField(db.ReferenceField('Category'))
    meta={
        'allow_inheritance': True,
        'ordering':['-timestamp']
    }

    @property
    def html_content(self):
        hilite=CodeHiliteExtension(linenums=False,css_class='highlight')
        extras=ExtraExtension()
        markdowm_content=markdown(self.content,extensions=[hilite,extras])
        oembed_content=parse_html(
            markdowm_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=800)
        return Markup(oembed_content)

    def __repr__(self):
        return '<Post %r>' %self.title

    def __unicode__(self):
        return self.title

'''后台管理'''
class PostAdmin(ModelView):
    form_base_class = Form
    column_display_pk = True
    can_create = False
    column_list = ('title','timestamp','published')


admin.add_view(PostAdmin(Post))
