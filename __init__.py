from django.core.cache import cache

# try:
#     from person.organize.unit.models import Units
# except:
#     Units = None
#
# try:
#     from person.organize.depart.models import Departs
# except:
#     Departs = None

class ENVManager():
    "定义一些常用的方法"
    def get(self, id):
        #获取机构常量配置
        const = cache.get('env')
        return const[id]

ENVManager = ENVManager()

from django import forms
from django.utils.safestring import mark_safe
#改变raido的显示形式，所有选项显示在一行。
class HorizRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))
