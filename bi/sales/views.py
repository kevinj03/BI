# -*- coding:utf-8 -*-
from django.db import connection,connections
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from apps.models import MineManager
import datetime
import calendar
from apps import Departs
from apps.utils import contrast
import settings


def stat_all_month(request):
    """
    描述：商务部数据月统计
    作者：凯伦kevin 2014年3月17日
    参数 : 无
    返回 : 无
    """
    EVENT_RIGHT = 1461
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    unit = Mine.Unit.id
    sunit=int(request.GET.get('sunit',unit))
    unit_list ='2,5,7,8,9,10'
    province=u'辽宁'
    if sunit in [3,11,12,13,14]:
        unit_list = '3,11,12,13,14'
        province=u'吉林'
    elif sunit in [4,15,16,17,18,19,20,21,22,23,24]:
        unit_list = '4,15,16,17,18,19,20,21,22,23,24'
        province=u'河北'
    sql1 = u'''
     select unid, uname as 地区, recevied_all as 实际回款, recevied_bd as 预存款实际销售额,tasknums as 新增单产任务,
    dl_bd as 新增单产,
    ( case
    when tasknums = 0 then 0
    else round(100*dl_bd/tasknums,2)
    end )
    as 单产任务完成率,
   round(DECODE(dc_hb,0,NULL,100*(dl_bd-dc_hb)/dc_hb) ,2) as 单产环比,
   round(DECODE(TB_DC,0,NULL,100*(dl_bd-TB_DC)/TB_DC),2) as 单产同比,
    pbcount as 商务人数,
    ( case
    when pcount = 0 then 0
    else round(100*pbcount/pcount,2)
    end )
    as 商务人数占比,
    ( case
    when pbcount=0 then 0
    else round(sales_bd/pbcount,2)
    end )
    as 人均创效,
    ( case when sales_bd_hb=0 or pbcount_hb=0 then 0
    else round(sales_bd_hb/pbcount_hb,2)
    end )
    as 人均创效环比绝对值,
    ( case
    when sales_bd_hb=0 or pbcount_hb=0 then 0
    else round(100*(
    (case when pbcount=0 then 0 else sales_bd/pbcount end)-sales_bd_hb/pbcount_hb)/(sales_bd_hb/pbcount_hb),2)
    end) as 人均创效环比率,
    srv_dl_pg as 盘古建站服务包单量,
    srv_pg as 盘古建站服务包金额,
    dl_pg as 盘古建站销售量,
    dl_dz as 定制网站单量,
    khcount as 百度开户单数总数,
    swkhcount as 商务开户数,
    sskhcount as 实施开户数,
    gckhcount as 归巢开户数,
    ( case
    when khcount = 0 then 0
    ELSE round(100*swkhcount/khcount,2)
    end )
    as 商务占比,
    ( case
    when khcount = 0 then 0
    else round(100*sskhcount/khcount,2)
    end )
    as 实施占比,
    ( case
    when khcount = 0 then 0
    else round(100*gckhcount/khcount,2)
    end )
    as 归巢占比,
    pcount,sales_bd,sales_bd_hb,pbcount_hb
    from STA_UNITPERFORMANCE_MONTH_VIEW
    where unid in ({2})
    and YYYY = '{0}'
    and MM = '{1}'
    order by unid
    '''.format(yy, mm,unit_list)
    sql = u'''
 with sql1 as({0})
  (select unid,地区,实际回款,预存款实际销售额,新增单产任务,新增单产,单产任务完成率,单产环比,单产同比,商务人数,
  商务人数占比,人均创效,人均创效环比绝对值,人均创效环比率,盘古建站服务包单量,盘古建站服务包金额,盘古建站销售量,定制网站单量,百度开户单数总数,商务开户数,
  实施开户数,归巢开户数,商务占比,实施占比,归巢占比 from sql1
  where unid <>{1})
  union all
  (select 100,N'{2}省分公司小计',sum(实际回款),sum(预存款实际销售额),sum(新增单产任务),sum(新增单产),
   ( case
    when sum(新增单产任务) = 0 then 0
    else round(100*sum(新增单产)/sum(新增单产任务),2)
    end ),
    round(DECODE(sum(单产环比),0,NULL,100*sum(新增单产-单产环比)/sum(单产环比)) ,2) as 单产环比,
    round(DECODE(sum(单产同比),0,NULL,100*sum(新增单产-单产同比)/sum(单产同比)),2) as 单产同比,
    sum(商务人数),
   ( case
    when sum(pcount) = 0 then 0
    else round(100*sum(商务人数)/sum(pcount),2)
    end ),
   ( case
    when sum(商务人数)=0 then 0
    else round(sum(sales_bd)/sum(商务人数),2)
    end ),
   ( case when sum(sales_bd_hb)=0 or sum(pbcount_hb)=0 then 0
    else round(sum(sales_bd_hb)/sum(pbcount_hb),2)
    end ),
   ( case
    when sum(sales_bd_hb)=0 or sum(pbcount_hb)=0 then 0
    else round(100*(
    (case when sum(商务人数)=0 then 0 else sum(sales_bd)/sum(商务人数) end)-sum(sales_bd_hb)/sum(pbcount_hb))/(sum(sales_bd_hb)/sum(pbcount_hb)),2)
    end),
    sum(盘古建站服务包单量),sum(盘古建站服务包金额),sum(盘古建站销售量),sum(定制网站单量),sum(百度开户单数总数),sum(商务开户数),sum(实施开户数),sum(归巢开户数),
    ( case
    when sum(百度开户单数总数) = 0 then 0
    ELSE round(100*sum(商务开户数)/sum(百度开户单数总数),2)
    end ),
    ( case
    when sum(百度开户单数总数) = 0 then 0
    else round(100*sum(实施开户数)/sum(百度开户单数总数),2)
    end ),
    ( case
    when sum(百度开户单数总数) = 0 then 0
    else round(100*sum(归巢开户数)/sum(百度开户单数总数),2)
    end )
    from sql1
    where unid <>{1}
  )
  union all
  (select 100,地区,实际回款,预存款实际销售额,新增单产任务,新增单产,单产任务完成率,单产环比,单产同比,商务人数,
  商务人数占比,人均创效,人均创效环比绝对值,人均创效环比率,盘古建站服务包单量,盘古建站服务包金额,盘古建站销售量,定制网站单量,百度开户单数总数,商务开户数,
  实施开户数,归巢开户数,商务占比,实施占比,归巢占比 from sql1
  where unid = {1})
  union all
  (select 200,N'{2}省总计',sum(实际回款),sum(预存款实际销售额),sum(新增单产任务),sum(新增单产),
   ( case
    when sum(新增单产任务) = 0 then 0
    else round(100*sum(新增单产)/sum(新增单产任务),2)
    end ),
    sum(单产环比),sum(单产同比),sum(商务人数),
   ( case
    when sum(pcount) = 0 then 0
    else round(100*sum(商务人数)/sum(pcount),2)
    end ),
   ( case
    when sum(商务人数)=0 then 0
    else round(sum(sales_bd)/sum(商务人数),2)
    end ),
   ( case when sum(sales_bd_hb)=0 or sum(pbcount_hb)=0 then 0
    else round(sum(sales_bd_hb)/sum(pbcount_hb),2)
    end ),
   ( case
    when sum(sales_bd_hb)=0 or sum(pbcount_hb)=0 then 0
    else round(100*(
    (case when sum(商务人数)=0 then 0 else sum(sales_bd)/sum(商务人数) end)-sum(sales_bd_hb)/sum(pbcount_hb))/(sum(sales_bd_hb)/sum(pbcount_hb)),2)
    end),
    sum(盘古建站服务包单量),sum(盘古建站服务包金额),sum(盘古建站销售量),sum(定制网站单量),sum(百度开户单数总数),sum(商务开户数),sum(实施开户数),sum(归巢开户数),
    ( case
    when sum(百度开户单数总数) = 0 then 0
    ELSE round(100*sum(商务开户数)/sum(百度开户单数总数),2)
    end ),
    ( case
    when sum(百度开户单数总数) = 0 then 0
    else round(100*sum(实施开户数)/sum(百度开户单数总数),2)
    end ),
    ( case
    when sum(百度开户单数总数) = 0 then 0
    else round(100*sum(归巢开户数)/sum(百度开户单数总数),2)
    end )
    from sql1
  )
    '''.format(sql1,sunit,province)
    cursor = connections['default'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': str(yy),
        'mm': mm,
        'mm1': str(mm1),
        'mm2': str(mm2),
        'yy1': str(yy1),
        'yy2': str(yy2),
        'opera': opera,
        'querys': querys,
        'unit':unit,
        'sunit':sunit
    }
    return render_to_response('bi_sales_all_month.html', context, context_instance=RequestContext(request))



def stat_all_week(request):
    """
    描述：商务部数据周统计
    作者：凯伦kevin 2014年3月21日
    参数 : 无
    返回 : 无
    """
    EVENT_RIGHT = 1457
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    ww = calendar.monthcalendar(int(yy), int(mm))
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    year1 = str(yy-1)
    year2 = str(yy+1)
    unit = Mine.Unit.id
    sunit=int(request.GET.get('sunit',unit))
    unit_list ='2,5,7,8,9,10'
    unit_list1 = '5,7,8,9,10'
    province = u'辽宁'
    if sunit in [3,11,12,13,14]:
        unit_list = '3,11,12,13,14'
        unit_list1 = '11,12,13,14'
        province=u'吉林'
    elif sunit in [4,15,16,17,18,19,20,21,22,23,24]:
        unit_list = '4,15,16,17,18,19,20,21,22,23,24'
        unit_list1 = '15,16,17,18,19,20,21,22,23,24'
        province=u'河北'
    datas =[]
    b = []
    cursor = connections["default"].cursor()
    wk = []
    for i in range(len(ww)):
        a = [x for x in ww[i] if x > 0]
        wk.append(a)
        k1 = wk[i][0]
        k2 = wk[i][len(wk[i])-1]
        sql1 = u'''
 SELECT aaa.id,aaa.name as 地区,月任务,员工人数, 百度单产,百度销售额,户均开户额,单产任务完成比,人均单产,盘古建站,定制网站,
 移动盘古建站, 定制移动建站, 移动建站总数,移动建站上线数,移动建站上线率,建单,移盘
  FROM units aaa
 LEFT OUTER JOIN
 (
       SELECT unid,  tasknums as 月任务, pcount as 员工人数, dl_bd as 百度单产, sales_bd as 百度销售额,
         ( case
         when dl_bd=0 then 0
         else round(sales_bd/dl_bd,2)
         end)
         as 户均开户额,
         ( case
         when tasknums = 0 then 0
         else round(100*dl_bd/tasknums,2)
         end )
         as 单产任务完成比,
         ( case
          when pcount = 0 then 0
          else round(sales_bd/pcount,2)
          end )
          as 人均单产,
          dl_pg as 盘古建站, dl_dz as 定制网站, dl_3g_pg as 移动盘古建站, dl_3g_dz as 定制移动建站,
          (dl_3g_pg + dl_3g_dz) as 移动建站总数,
          dl_3g_sx as 移动建站上线数,
          ( case
          when (dl_3g_pg + dl_3g_dz) = 0 then 0
          else round(100*dl_3g_sx/(dl_3g_pg + dl_3g_dz),2)
          end )
          as 移动建站上线率,
         ( case
          when dl_bd = 0 then 0
          else round(100*(dl_3g_pg + dl_3g_dz)/dl_bd,2)
          end )
          as 建单,
          ( case
           when dl_pg = 0 then 0
           else round(100*(dl_3g_pg + dl_3g_dz)/dl_pg,2)
           end )
           as 移盘
         FROM STA_UNITPERFORMANCE_WEEK
        where
        yyyy={0} and mm={1} and ww={2}
        ) bbb
        ON aaa.id=bbb.unid
        WHERE aaa.id IN    ({3})
        order by id
        '''.format(yy, mm, i+1, unit_list)
        sql = u'''
           with sql1 as ({0})
           (select id,地区,月任务,员工人数,百度单产,百度销售额,户均开户额,单产任务完成比,人均单产,盘古建站,定制网站,
           移动盘古建站,定制移动建站,移动建站总数,移动建站上线数,移动建站上线率,建单,移盘
           from sql1 )
           union all
           (select 100, N'{2}省分公司小计',sum(月任务),sum(员工人数),sum(百度单产),sum(百度销售额),
           ( case
         when sum(百度单产)=0 then 0
         else round(sum(百度销售额)/sum(百度单产),2)
         end),
           ( case
         when sum(月任务) = 0 then 0
         else round(100*sum(百度单产)/sum(月任务),2)
         end ),
         ( case
          when sum(员工人数) = 0 then 0
          else round(sum(百度销售额)/sum(员工人数),2)
          end ),
          sum(盘古建站),sum(定制网站),sum(移动盘古建站),sum(定制移动建站),sum(移动建站总数),sum(移动建站上线数),
          ( case
          when sum(移动建站总数) = 0 then 0
          else round(100*sum(移动建站上线数)/sum(移动建站总数),2)
          end ),
          ( case
          when sum(百度单产) = 0 then 0
          else round(100*sum(移动建站总数)/sum(百度单产),2)
          end ),
          ( case
           when sum(盘古建站) = 0 then 0
           else round(100*sum(移动建站总数)/sum(盘古建站),2)
           end )
           from sql1
           where id in ({1}))
           union all
           (select 200, N'{2}省总计',sum(月任务),sum(员工人数),sum(百度单产),sum(百度销售额),
           ( case
         when sum(百度单产)=0 then 0
         else round(sum(百度销售额)/sum(百度单产),2)
         end),
           ( case
         when sum(月任务) = 0 then 0
         else round(100*sum(百度单产)/sum(月任务),2)
         end ),
         ( case
          when sum(员工人数) = 0 then 0
          else round(sum(百度销售额)/sum(员工人数),2)
          end ),
          sum(盘古建站),sum(定制网站),sum(移动盘古建站),sum(定制移动建站),sum(移动建站总数),sum(移动建站上线数),
          ( case
          when sum(移动建站总数) = 0 then 0
          else round(100*sum(移动建站上线数)/sum(移动建站总数),2)
          end ),
          ( case
          when sum(百度单产) = 0 then 0
          else round(100*sum(移动建站总数)/sum(百度单产),2)
          end ),
          ( case
           when sum(盘古建站) = 0 then 0
           else round(100*sum(移动建站总数)/sum(盘古建站),2)
           end )
           from sql1)
           '''.format(sql1, unit_list1, province)
        cursor.execute(sql)
        querys = cursor.fetchall()
        rowspan = len(querys)
        j = 0
        for q in querys:
            data = {}
            if j == 0:
                data["time"] = u'第{0}周({1}日至{2}日)'.format(i+1, k1, int(k2))
                data["rowspan"] = rowspan
            data["unid"] = q[0]
            data["unit"] = q[1]
            data["tasknums"] = q[2]
            data["pcount"] = q[3]
            data["dl_bd"] = q[4]
            data["sales_bd"] = q[5]
            data["hjkhe"] = q[6]
            data["dcrwwcb"] = q[7]
            data["rjdc"] = q[8]
            data["dl_pg"] = q[9]
            data["dl_dz"] = q[10]
            data["dl_3g_pg"] = q[11]
            data["dl_3g_dz"] = q[12]
            data["ydjzzs"] = q[13]
            data["dl_3g_sx"] = q[14]
            data["ydjzsxl"] = q[15]
            data["yd_dc"] = q[16]
            data["yd_jz"] = q[17]
            datas.append(data)
            j = j+1
    sql2 = u'''
        SELECT unid,uname as 地区, avg(tasknums) as 月任务, avg(pcount) as 员工人数, sum(dl_bd) as 百度单产, sum(sales_bd) as 百度销售额,
         ( case
         when sum(dl_bd)=0 then 0
         else round(sum(sales_bd)/sum(dl_bd),2)
         end)
         as 户均开户额,
         ( case
         when avg(tasknums) = 0 then 0
         else round(100*sum(dl_bd)/avg (tasknums),2)
         end )
         as 单产任务完成比,
         ( case
          when avg(pcount) = 0 then 0
          else round(sum(sales_bd)/avg(pcount),2)
          end )
          as 人均单产,
          sum(dl_pg) as 盘古建站, sum(dl_dz) as 定制网站, sum(dl_3g_pg) as 移动盘古建站, sum(dl_3g_dz) as 定制移动建站,
          sum(dl_3g_pg + dl_3g_dz) as 移动建站总数,
          sum(dl_3g_sx) as 移动建站上线数,
          ( case
          when sum((dl_3g_pg + dl_3g_dz)) = 0 then 0
          else round(100*sum(dl_3g_sx)/sum((dl_3g_pg + dl_3g_dz)),2)
          end )
          as 移动建站上线率,
         ( case
          when sum(dl_bd) = 0 then 0
          else round(100*sum((dl_3g_pg + dl_3g_dz))/sum(dl_bd),2)
          end )
          as 建单,
          ( case
           when sum(dl_pg) = 0 then 0
           else round(100*sum((dl_3g_pg+dl_3g_dz))/sum(dl_pg),2)
           end )
           as 移盘
           from STA_UNITPERFORMANCE_WEEK
           where unid in ({2})
           and yyyy = {0} and mm={1}
           group by mm,yyyy,uname,unid
           order by unid
           '''.format(yy, mm, unit_list)
    sql = u'''
       with sql2 as ({0})
       (select unid,地区,月任务,员工人数,百度单产,百度销售额,户均开户额,单产任务完成比,人均单产,盘古建站,定制网站,
           移动盘古建站,定制移动建站,移动建站总数,移动建站上线数,移动建站上线率,建单,移盘
           from sql2)
        union all
         (SELECT 100,N'{2}省分公司小计', sum(月任务), sum(员工人数), sum(百度单产), sum(百度销售额),
         ( case
         when sum(百度单产)=0 then 0
         else round(sum(百度销售额)/sum(百度单产),2)
         end)
         as 户均开户额,
         ( case
         when sum(月任务) = 0 then 0
         else round(100*sum(百度单产)/sum(月任务),2)
         end )
         as 单产任务完成比,
         ( case
          when sum(员工人数) = 0 then 0
          else round(sum(百度销售额)/sum(员工人数),2)
          end )
          as 人均单产,
          sum(盘古建站), sum(定制网站), sum(移动盘古建站), sum(定制移动建站),
          sum(移动建站总数),
          sum(移动建站上线数),
          ( case
          when sum(移动建站总数) = 0 then 0
          else round(100*sum(移动建站上线数)/sum(移动建站上线数),2)
          end ),
         ( case
          when sum(百度单产) = 0 then 0
          else round(100*sum(移动建站总数)/sum(百度单产),2)
          end )
          as 建单,
          ( case
           when sum(盘古建站) = 0 then 0
           else round(100*sum(移动建站总数)/sum(盘古建站),2)
           end )
           as 移盘
           from sql2
           where unid in ({1}))
           union all
           (SELECT 200,N'{2}省总计', sum(月任务), sum(员工人数), sum(百度单产), sum(百度销售额),
         ( case
         when sum(百度单产)=0 then 0
         else round(sum(百度销售额)/sum(百度单产),2)
         end),
         ( case
         when sum(月任务) = 0 then 0
         else round(100*sum(百度单产)/sum(月任务),2)
         end ),
         ( case
          when sum(员工人数) = 0 then 0
          else round(sum(百度销售额)/sum(员工人数),2)
          end )
          as 人均单产,
          sum(盘古建站), sum(定制网站), sum(移动盘古建站), sum(定制移动建站),
          sum(移动建站总数),
          sum(移动建站上线数),
          ( case
          when sum(移动建站总数) = 0 then 0
          else round(100*sum(移动建站上线数)/sum(移动建站总数),2)
          end ),
         ( case
          when sum(百度单产) = 0 then 0
          else round(100*sum(移动建站总数)/sum(百度单产),2)
          end )
          as 建单,
          ( case
           when sum(盘古建站) = 0 then 0
           else round(100*sum(移动建站总数)/sum(盘古建站),2)
           end )
           as 移盘
           from sql2)
        '''.format(sql2, unit_list1, province)
    cursor.execute(sql)
    querys = cursor.fetchall()
    rowspan = len(querys)
    j = 0
    for q in querys:
        data = {}
        if j == 0:
            data["time"] = u'{0}月合计'.format(mm)
            data['rowspan'] = rowspan
        data["unid"] = q[0]
        data["unit"] = q[1]
        data["tasknums"] = q[2]
        data["pcount"] = q[3]
        data["dl_bd"] = q[4]
        data["sales_bd"] = q[5]
        data["hjkhe"] = q[6]
        data["dcrwwcb"] = q[7]
        data["rjdc"] = q[8]
        data["dl_pg"] = q[9]
        data["dl_dz"] = q[10]
        data["dl_3g_pg"] = q[11]
        data["dl_3g_dz"] = q[12]
        data["ydjzzs"] = q[13]
        data["dl_3g_sx"] = q[14]
        data["ydjzsxl"] = q[15]
        data["yd_dc"] = q[16]
        data["yd_jz"] = q[17]
        datas.append(data)
        j = j+1
    context = {
        'yy': str(yy),
        'year1': year1,
        'year2': year2,
        'opera': opera,
        'datas': datas,
        'mm': mm,
        'mm1': mm1,
        'mm2': mm2,
        'yy1': yy1,
        'yy2': yy2,
        'a': a,
        'unit':unit,
        'sunit':sunit
    }
    return render_to_response('bi_sales_all_week.html', context, context_instance=RequestContext(request))


def wstat_wxrwwc(request, context):
    """
    描述：网销任务完成情况统计
    作者：凯伦kevin  2014年1月20日
    """
    EVENT_RIGHT = 1453
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)

    if type(opera) == type(''):
        return HttpResponse(opera)
    '''
    权限验证结束
    '''
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    # wd = calendar.weekday(yy, 1, 1)
    # if wd:
    #     ww = int(datetime.datetime.now().strftime('%W'))+1
    # else:
    #     ww = int(datetime.datetime.now().strftime('%W'))
    # if ww > 52:
    #     ww = 1
    # q = range(1, 53)
    #
    # ww = request.GET.get('week', ww)
    # wd = calendar.weekday(int(yy), 1, 1)
    # start = datetime.datetime(int(yy), 1, 1)+datetime.timedelta(days=(int(ww)-2)*7+(7-wd))
    # over = datetime.datetime(int(yy), 1, 1)+datetime.timedelta(days=(int(ww)-2)*7+(7-wd)+6)
    # start = start.strftime("%Y-%m-%d")
    # over = over.strftime("%Y-%m-%d")
    # statype = int(request.GET.get('statype', 1))
    # if statype == 1:
    #     a = 'M'+str.rjust(str(mm), 2, '0')+'CY'+str(yy)
    # else:
    #     a = 'WK'+str.rjust(str(ww), 2, '0')+'CY'+str(yy)
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    # if str(ww) == '1':
    #     w1 = 52
    #     y1 = int(yy)-1
    # else:
    #     w1 = int(ww)-1
    #     y1 = int(yy)
    # if str(ww) == '52':
    #     w2 = 1
    #     y2 = int(yy)+1
    # else:
    #     w2 = int(ww)+1
    #     y2 = int(yy)
    sql = u'''
   select t.UNIT,u.SHORT_DESCRIPTION,t.ZDC,t.PC_MONEY,t.YD_MONEY,t.TASKMONEY,t.WCXSE,t.YJWCL,t.RJXSE,t.PCAVG,t.YDAVG,
   u.LEVEL_NAME from WXRWWC_CUBE_VIEW t
    LEFT JOIN UNIT_STATISTICS_VIEW u on t.UNIT=u.dim_key
    WHERE t.TIME='M{0}CY{1}' AND u.LEVEL_NAME='UNIT'
    AND u.SYSTEM='{2}'
    ORDER BY u.HIER_ORDER DESC
    '''.format(str.rjust(str(mm), 2, '0'), yy,settings.SYSTEM_KEY)
    cursor = connections['bi'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': str(yy),
        'mm': str(mm),
        'yy1': str(yy1),
        'mm1': str(mm1),
        'yy2': str(yy2),
        'mm2': str(mm2),
        'querys': querys,
        'opera': opera,
    }
    return render_to_response('bi_sales_wxrwwc.html', context)



def stat_jgyjtj(request,context):
    """
    描述：机构业绩统计
    作者：凯伦kevin  2014年3月27日
    参数 : 无
    返回 : 无
    """

    EVENT_RIGHT = 1454

    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)

    if type(opera) == type(''):
        return HttpResponse(opera)
    '''
    权限验证结束
    '''
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    q = (mm+2)/3
    q = int(request.GET.get('quarter', q))
    statype = int(request.GET.get('statype', 1))
    year1 = str(yy-1)
    year2 = str(yy+1)
    if str(yy) == '2017':
        year2 = '2017'
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    if str(q) == '1':
        q1 = 4
        y1 = int(yy)-1
    else:
        q1 = int(q)-1
        y1 = int(yy)
    if str(q) == '4':
        q2 = 1
        y2 = int(yy)+1
    else:
        q2 = int(q)+1
        y2 = int(yy)
    time = ''
    if statype == 1:
        time = "and mm = {1}".format(yy, mm)
    elif statype == 2:
        time = "and mm in ({1},{2},{3})".format(yy, q*3-2,q*3-1,q*3 )
    unit = Mine.Unit.id
    unit_list ='2,5,7,8,9,10'
    province=u'辽宁'
    if Mine.Unit.id in [3,11,12,13,14]:
        unit_list = '3,11,12,13,14'
        province=u'吉林'
    elif Mine.Unit.id in [4,15,16,17,18,19,20,21,22,23,24]:
        unit_list = '4,15,16,17,18,19,20,21,22,23,24'
        province=u'河北'
    cursor = connections['default'].cursor()
    sql1 = u'''
   SELECT aaa.id,aaa.name,bbb.员工人数,bbb.单数任务,bbb.预存款完成,bbb.单数完成,
    round(DECODE(bbb.单数任务,0,NULL,bbb.单数完成*100/bbb.单数任务),2),
    ROUND(bbb.预存款完成/bbb.单数完成,2),
    round(DECODE(bbb.员工人数,0,NULL,bbb.单数完成/bbb.员工人数),2),
    round(DECODE(bbb.员工人数,0,NULL,bbb.预存款完成/bbb.员工人数),2)
    FROM units aaa
    LEFT JOIN (select unid,sum(tasknums) as 单数任务,sum(money_done) as 预存款完成,round(avg(pcount)) as 员工人数,sum(num_done) as 单数完成 from sta_jgyjtj
    where yyyy = {0} {1} group by unid) bbb
    ON aaa.id=bbb.unid
    where id in ({2})
    ORDER BY id
    '''.format(yy, time, unit_list)
    sql2 = u'''
    with sql1 as ({0})
    select sum(单数完成) from sql1
    '''.format(sql1)
    cursor.execute(sql2)
    querys = cursor.fetchall()
    aa = querys[0][0]
    if  not aa:
        aa = 0
    sql = u'''
    with sql1 as ({0})
    (select t.*,round(decode({3}, 0, NULL, 100*单数完成/{3}),2) from sql1 t)
    union all
    (select 100,N'{1}省总计', sum(员工人数),sum(单数任务),sum(预存款完成),sum(单数完成),
    round(DECODE(sum(单数任务),0,NULL,sum(单数完成)*100/sum(单数任务)),2),
    ROUND(DECODE(sum(单数完成),0,NULL,SUM(预存款完成)/SUM(单数完成)),2),
    round(DECODE(sum(员工人数),0,NULL,sum(单数完成)/sum(员工人数)),2),
    round(DECODE(sum(员工人数),0,NULL,sum(预存款完成)/sum(员工人数)),2),
    NULL
    from sql1
    where id in ({2}))
    '''.format(sql1, province,unit_list, aa)
    cursor.execute(sql)
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    querys = row
    context = {
        'yy': str(yy),
        'mm': str(mm),
        'q': str(q),
        'yy1': str(yy1),
        'mm1': str(mm1),
        'yy2': str(yy2),
        'mm2': str(mm2),
        'y1': str(y1),
        'y2': str(y2),
        'year1': str(year1),
        'year2': str(year2),
        'statype': str(statype),
        'querys': querys,
        'opera': opera,
        'q1': str(q1),
        'q2': str(q2)
    }
    return render_to_response('bi_sales_jgyjtj.html', context)



def wstat_jcswyjtj(request, context):
    """
    描述：基础商务业绩统计
    作者：凯伦kevin  2014年1月21日
    """

    EVENT_RIGHT = 1455

    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)

    if type(opera) == type(''):
        return HttpResponse(opera)
    '''
    权限验证结束
    '''
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    q = (mm+2)/3
    q = int(request.GET.get('quarter', q))
    statype = int(request.GET.get('statype', 1))
    year1 = str(yy-1)
    year2 = str(yy+1)
    if str(yy) == '2017':
        year2 = '2017'
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    if str(q) == '1':
        q1 = 4
        y1 = int(yy)-1
    else:
        q1 = int(q)-1
        y1 = int(yy)
    if str(q) == '4':
        q2 = 1
        y2 = int(yy)+1
    else:
        q2 = int(q)+1
        y2 = int(yy)
    time = ''
    if statype == 1:
        time = "and mm = {1}".format(yy, mm)
    elif statype == 2:
        time = "and mm in ({1},{2},{3})".format(yy, q*3-2,q*3-1,q*3 )
    unit = Mine.Unit.id
    unit_list ='2,5,7,8,9,10'
    province=u'辽宁'
    if Mine.Unit.id in [3,11,12,13,14]:
        unit_list = '3,11,12,13,14'
        province=u'吉林'
    elif Mine.Unit.id in [4,15,16,17,18,19,20,21,22,23,24]:
        unit_list = '4,15,16,17,18,19,20,21,22,23,24'
        province=u'河北'
    cursor = connections['default'].cursor()
    sql1 = u'''
   SELECT aaa.id,aaa.name,bbb.员工人数,bbb.单数任务,bbb.预存款完成,bbb.单数完成,
    round(DECODE(bbb.单数任务,0,NULL,bbb.单数完成*100/bbb.单数任务),2),
    ROUND(bbb.预存款完成/bbb.单数完成,2),
    round(DECODE(bbb.员工人数,0,NULL,bbb.单数完成/bbb.员工人数),2),
    round(DECODE(bbb.员工人数,0,NULL,bbb.预存款完成/bbb.员工人数),2)
    FROM units aaa
    LEFT JOIN (select unid,sum(tasknums) as 单数任务,sum(money_done) as 预存款完成,avg(pcount) as 员工人数,sum(num_done) as 单数完成 from sta_jcswyjtj
    where yyyy = {0} {1} group by unid) bbb
    ON aaa.id=bbb.unid
    where id in ({2})
    ORDER BY id
    '''.format(yy, time, unit_list)
    sql = u'''
    with sql1 as ({0})
    (select * from sql1)
    union all
    (select 100,N'{1}省总计', sum(员工人数),sum(单数任务),sum(预存款完成),sum(单数完成),
    round(DECODE(sum(单数任务),0,NULL,sum(单数完成)*100/sum(单数任务)),2),
    ROUND(DECODE(sum(单数完成),0,NULL,SUM(预存款完成)/SUM(单数完成)),2),
    round(DECODE(sum(员工人数),0,NULL,sum(单数完成)/sum(员工人数)),2),
    round(DECODE(sum(员工人数),0,NULL,sum(预存款完成)/sum(员工人数)),2)
    from sql1
    where id in ({2}))
    '''.format(sql1, province,unit_list)
    print sql
    cursor.execute(sql)
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    querys = row
    context = {
        'yy': str(yy),
        'mm': str(mm),
        'q': str(q),
        'yy1': str(yy1),
        'mm1': str(mm1),
        'yy2': str(yy2),
        'mm2': str(mm2),
        'y1': str(y1),
        'y2': str(y2),
        'year1': str(year1),
        'year2': str(year2),
        'statype': str(statype),
        'querys': querys,
        'opera': opera,
        'q1': str(q1),
        'q2': str(q2)
    }
    return render_to_response('bi_sales_jcswyjtj.html', context)


def wstat_ssyxyjtj(request, context):
    """
    描述：搜索营销业绩统计
    作者：凯伦kevin  2014年1月21日
    """

    EVENT_RIGHT = 1456

    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)

    if type(opera) == type(''):
        return HttpResponse(opera)
    '''
    权限验证结束
    '''
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    q = (mm+2)/3
    q = int(request.GET.get('quarter', q))
    statype = int(request.GET.get('statype', 1))
    year1 = str(yy-1)
    year2 = str(yy+1)
    if str(yy) == '2017':
        year2 = '2017'
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    if str(q) == '1':
        q1 = 4
        y1 = int(yy)-1
    else:
        q1 = int(q)-1
        y1 = int(yy)
    if str(q) == '4':
        q2 = 1
        y2 = int(yy)+1
    else:
        q2 = int(q)+1
        y2 = int(yy)
    time = ''
    if statype == 1:
        time = "and mm = {1}".format(yy, mm)
    elif statype == 2:
        time = "and mm in ({1},{2},{3})".format(yy, q*3-2,q*3-1,q*3 )
    unit = Mine.Unit.id
    unit_list ='2,5,7,8,9,10'
    province=u'辽宁'
    if Mine.Unit.id in [3,11,12,13,14]:
        unit_list = '3,11,12,13,14'
        province=u'吉林'
    elif Mine.Unit.id in [4,15,16,17,18,19,20,21,22,23,24]:
        unit_list = '4,15,16,17,18,19,20,21,22,23,24'
        province=u'河北'
    cursor = connections['default'].cursor()
    sql1 = u'''
   SELECT aaa.id,aaa.name,bbb.员工人数,bbb.单数任务,bbb.预存款完成,bbb.单数完成,
    round(DECODE(bbb.单数任务,0,NULL,bbb.单数完成*100/bbb.单数任务),2),
    ROUND(bbb.预存款完成/bbb.单数完成,2),
    round(DECODE(bbb.员工人数,0,NULL,bbb.单数完成/bbb.员工人数),2),
    round(DECODE(bbb.员工人数,0,NULL,bbb.预存款完成/bbb.员工人数),2)
    FROM units aaa
    LEFT JOIN (select unid,sum(tasknums) as 单数任务,sum(money_done) as 预存款完成,avg(pcount) as 员工人数,sum(num_done) as 单数完成 from sta_ssyxyjtj
    where yyyy = {0} {1} group by unid) bbb
    ON aaa.id=bbb.unid
    where id in ({2})
    ORDER BY id
    '''.format(yy, time, unit_list)
    sql = u'''
    with sql1 as ({0})
    (select * from sql1)
    union all
    (select 100,N'{1}省总计', sum(员工人数),sum(单数任务),sum(预存款完成),sum(单数完成),
    round(DECODE(sum(单数任务),0,NULL,sum(单数完成)*100/sum(单数任务)),2),
    ROUND(DECODE(sum(单数完成),0,NULL,SUM(预存款完成)/SUM(单数完成)),2),
    round(DECODE(sum(员工人数),0,NULL,sum(单数完成)/sum(员工人数)),2),
    round(DECODE(sum(员工人数),0,NULL,sum(预存款完成)/sum(员工人数)),2)
    from sql1
    where id in ({2}))
    '''.format(sql1, province,unit_list)
    print sql
    cursor.execute(sql)
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    querys = row
    context = {
        'yy': str(yy),
        'mm': str(mm),
        'q': str(q),
        'yy1': str(yy1),
        'mm1': str(mm1),
        'yy2': str(yy2),
        'mm2': str(mm2),
        'y1': str(y1),
        'y2': str(y2),
        'year1': str(year1),
        'year2': str(year2),
        'statype': str(statype),
        'querys': querys,
        'opera': opera,
        'q1': str(q1),
        'q2': str(q2)
    }
    return render_to_response('bi_sales_ssyxyjtj.html', context)


def wstat_zjxstj(request, context):
    """
    描述：最佳销售统计
    作者：凯伦kevin 2014年1月22日
    """
    EVENT_RIGHT = 1462
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    q = (mm+2)/3
    q = int(request.GET.get('quarter', q))
    statype = int(request.GET.get('statype', 1))
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)
    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)

    if str(q) == '1':
        q1 = 4
        y1 = yy-1
    else:
        q1 = int(q)-1
        y1 = yy
    if str(q) == '4':
        q2 = 1
        y2 = yy+1
    else:
        q2 = int(q)+1
        y2 = yy
    if statype == 1:
        sql = u'''
       --员工编号  员工名称  所属机构名称  单数完成
        select account, realname, uname, dswc, lastdt from sta_bestsales
        WHERE yyyy = {0} and mm = {1}
        ORDER BY dswc desc, lastdt asc
        '''.format(yy, mm)
    elif statype == 2:
        sql = u'''
        select account, realname, uname, sum(dswc) as dswc, max(lastdt) as lastdt from sta_bestsales
        where yyyy = {0} and mm in ({1},{2},{3})
        group by account, realname, uname
        order by dswc desc, lastdt asc
        '''.format(yy , q*3-2,q*3-1,q*3)
    cursor = connections['default'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()[:10]
    cursor.close()
    connection.close()
    context = {
        'yy': str(yy),
        'mm': str(mm),
        'q': str(q),
        'yy1': str(yy1),
        'mm1': str(mm1),
        'yy2': str(yy2),
        'mm2': str(mm2),
        'y1': str(y1),
        'y2': str(y2),
        'statype': str(statype),
        'querys': querys,
        'opera': opera,
        'q1': str(q1),
        'q2': str(q2)
    }
    return render_to_response('bi_sales_zjxstj.html', context, context_instance=RequestContext(request))


def wstat_ydyjdctj(request, context):
    """
    描述：月度业绩达成统计
    作者：凯伦kevin 2014年1月22日
    """
    EVENT_RIGHT = 1464
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    unit = Mine.Unit.id
    unit_list ='2,5,7,8,9,10'
    province=u'辽宁'
    if Mine.Unit.id in [3,11,12,13,14]:
        unit_list = '3,11,12,13,14'
        province=u'吉林'
    elif Mine.Unit.id in [4,15,16,17,18,19,20,21,22,23,24]:
        unit_list = '4,15,16,17,18,19,20,21,22,23,24'
        province=u'河北'
    sql1 = u'''
    SELECT aaa.id,aaa.name,bbb.员工人数, bbb.预存款完成,bbb.单数完成,
    round(DECODE(bbb.员工人数,0,NULL,bbb.单数完成/bbb.员工人数),2) as 人均单产,
    round(DECODE(bbb.员工人数,0,NULL,bbb.预存款完成/bbb.员工人数),2) as 人均创效,
    round(DECODE(bbb.单数完成,0,NULL,bbb.预存款完成/bbb.单数完成),2) as 户均开户额,
    round(DECODE(bbb.销售线索,0,NULL,100*bbb.单数完成/bbb.销售线索),2) as 销售线索统计,
    round(DECODE(ccc.dc_hb,0,NULL,100*(ccc.dl_bd-ccc.dc_hb)/ccc.dc_hb) ,2) as 单产环比,
    round(DECODE(ccc.TB_DC,0,NULL,100*(ccc.dl_bd-ccc.TB_DC)/ccc.TB_DC),2) as 单产同比,
    round(DECODE(SALES_BD_HB,0,NULL,100*(sales_bd-SALES_BD_HB)/SALES_BD_HB),2) as 销售额环比,
    round(DECODE(SALES_BD_TB,0,NULL,100*(sales_bd-SALES_BD_TB)/SALES_BD_TB),2) as 销售额同比,
    bbb.sxsj as 上线数据,销售线索,ccc.dc_hb,ccc.dl_bd,ccc.tb_dc,ccc.sales_bd_hb,ccc.sales_bd,ccc.sales_bd_tb
    FROM units aaa
    left JOIN (select unid,money_done as 预存款完成,pcount as 员工人数,num_done as 单数完成, xsxs as 销售线索, sxsj from sta_jgyjtj
     where yyyy = {0} and mm = {1}) bbb
    ON aaa.id=bbb.unid
    left join sta_unitperformance_month_view ccc
    on aaa.id = ccc.unid
    where id in ({2}) and yyyy = {0} and mm = {1}
    ORDER BY id
    '''.format(yy, mm, unit_list)
    sql = u'''
    with sql1 as ({0})
    (select id,name,员工人数,预存款完成,单数完成,人均单产,人均创效,户均开户额,销售线索统计,单产环比,单产同比,
    销售额环比,销售额同比,上线数据 from sql1)
    union all
    (select 100, N'{1}省总计',sum(员工人数),sum(预存款完成),sum(单数完成),
    round(DECODE(sum(员工人数),0,NULL,sum(单数完成)/sum(员工人数)),2) as 人均单产,
    round(DECODE(sum(员工人数),0,NULL,sum(预存款完成)/sum(员工人数)),2) as 人均创效,
    round(DECODE(sum(单数完成),0,NULL,sum(预存款完成)/sum(单数完成)),2) as 户均开户额,
    round(DECODE(sum(销售线索),0,NULL,100*sum(单数完成)/sum(销售线索)),2) as 销售线索统计,
    round(DECODE(sum(dc_hb),0,NULL,100*sum(dl_bd-dc_hb)/sum(dc_hb)) ,2) as 单产环比,
    round(DECODE(sum(TB_DC),0,NULL,100*sum(dl_bd-TB_DC)/sum(TB_DC)),2) as 单产同比,
    round(DECODE(sum(SALES_BD_HB),0,NULL,100*sum(sales_bd-SALES_BD_HB)/sum(SALES_BD_HB)),2) as 销售额环比,
    round(DECODE(sum(SALES_BD_TB),0,NULL,100*sum(sales_bd-SALES_BD_TB)/sum(SALES_BD_TB)),2) as 销售额同比,
    sum(上线数据) from sql1
    where id in ({2}))
    '''.format(sql1, province, unit_list)
    cursor = connections['default'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': yy,
        'mm': mm,
        'yy1': yy1,
        'mm1': mm1,
        'yy2': yy2,
        'mm2': mm2,
        'opera': opera,
        'querys': querys
    }
    return render_to_response('bi_sales_ydyjdctj.html', context, context_instance=RequestContext(request))


def wstat_qdhyzb(request, context):
    """
    描述：月度机构签单行业占比
    作者：凯伦kevin 2014年1月22日
    """
    EVENT_RIGHT = 1464
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    a = request.GET.get('a')
    b = request.GET.get('b')
    mm = request.GET.get('c')
    yy = request.GET.get('d')
    sql = u'''
   select b.INDUSTRY1,b.INDUSTRY1_SHORT_DESCRIPT,b.LEVEL_NAME,a.YJ,a.HYZB
   from UNIT_INDUSTRY_YJ_CUBE_VIEW a
    INNER JOIN industry_industrys_view b
    ON a.INDUSTRY=b.DIM_KEY
    WHERE TIME='M{0}CY{1}'
    AND b.LEVEL_NAME ='INDUSTRY1'
    AND UNIT='{2}'
    '''.format(str.rjust(str(mm), 2, '0'), yy, b)
    cursor = connections['bi'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': yy,
        'mm': mm,
        'opera': opera,
        'querys': querys,
        'a': a,
        'b': b,
        'mm': mm,
        'yy': yy
    }
    return render_to_response('bi_sales_qdhyzb.html', context, context_instance=RequestContext(request))


def wstat_rznxrjdctj(request, context):
    """
    描述：入职年限人均单产统计
    作者：凯伦kevin 2014年1月22日
    """
    EVENT_RIGHT = 1465
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    unit = Mine.Unit.id
    unit_list ='2,5,7,8,9,10'
    province=u'辽宁'
    if Mine.Unit.id in [3,11,12,13,14]:
        unit_list = '3,11,12,13,14'
        province=u'吉林'
    elif Mine.Unit.id in [4,15,16,17,18,19,20,21,22,23,24]:
        unit_list = '4,15,16,17,18,19,20,21,22,23,24'
        province=u'河北'
    sql1 = u'''
   select aaa.id,aaa.name,
   bbb.SW_M1,bbb.M1_DONE,
   ROUND(DECODE(ccc.NUM_DONE,0,NULL,bbb.M1_DONE*100/ccc.NUM_DONE),2),
   ROUND(DECODE(bbb.SW_M1,0,NULL,bbb.M1_DONE/bbb.SW_M1),2),
   bbb.SW_M1TO3,bbb.M1TO3_DONE,
   ROUND(DECODE(ccc.NUM_DONE,0,NULL,bbb.M1TO3_DONE*100/ccc.NUM_DONE),2),
   ROUND(DECODE(bbb.SW_M1TO3,0,NULL,bbb.M1TO3_DONE/bbb.SW_M1TO3),2),
   bbb.SW_M3TO6,bbb.M3TO6_DONE,
   ROUND(DECODE(ccc.NUM_DONE,0,NULL,bbb.M3TO6_DONE*100/ccc.NUM_DONE),2),
   ROUND(DECODE(bbb.SW_M3TO6,0,NULL,bbb.M3TO6_DONE/bbb.SW_M3TO6),2),
   bbb.SW_M6TO12,bbb.M6TO12_DONE,
   ROUND(DECODE(ccc.NUM_DONE,0,NULL,bbb.M6TO12_DONE*100/ccc.NUM_DONE),2),
   ROUND(DECODE(bbb.SW_M6TO12,0,NULL,bbb.M6TO12_DONE/bbb.SW_M6TO12),2),
   bbb.SW_M12TO24,bbb.M12TO24_DONE,
   ROUND(DECODE(ccc.NUM_DONE,0,NULL,bbb.M12TO24_DONE*100/ccc.NUM_DONE),2),
   ROUND(DECODE(bbb.SW_M12TO24,0,NULL,bbb.M12TO24_DONE/bbb.SW_M12TO24),2),
   bbb.SW_M24,bbb.M24_DONE,
   ROUND(DECODE(ccc.NUM_DONE,0,NULL,bbb.M24_DONE*100/ccc.NUM_DONE),2),
   ROUND(DECODE(bbb.SW_M24,0,NULL,bbb.M24_DONE/bbb.SW_M24),2),
   NUM_DONE
   FROM sta_rznxrjdc bbb LEFT JOIN units aaa
   ON aaa.id = bbb.unid
   LEFT JOIN sta_jgyjtj ccc
   ON bbb.unid = ccc.unid and bbb.yyyy = ccc.yyyy and bbb.mm = ccc.mm
   WHERE bbb.yyyy = {0} and bbb.mm = {1}
   AND id in ({2})
   ORDER BY id
    '''.format(yy,mm,unit_list)
    sql = u'''
    with sql1 as ({0})
    select * from sql1
    union all
    select 100,N'{1}省总计',
    sum(SW_M1),sum(M1_DONE),
    ROUND(DECODE(SUM(NUM_DONE),0,NULL,SUM(M1_DONE)*100/SUM(NUM_DONE)),2),
    ROUND(DECODE(SUM(SW_M1),0,NULL,SUM(M1_DONE)/SUM(SW_M1)),2),
    sum(SW_M1TO3),sum(M1TO3_DONE),
    ROUND(DECODE(SUM(NUM_DONE),0,NULL,SUM(M1TO3_DONE)*100/SUM(NUM_DONE)),2),
    ROUND(DECODE(SUM(SW_M1TO3),0,NULL,SUM(M1TO3_DONE)/SUM(SW_M1TO3)),2),
    sum(SW_M3TO6),sum(M3TO6_DONE),
    ROUND(DECODE(SUM(NUM_DONE),0,NULL,SUM(M3TO6_DONE)*100/SUM(NUM_DONE)),2),
    ROUND(DECODE(SUM(SW_M3TO6),0,NULL,SUM(M3TO6_DONE)/SUM(SW_M3TO6)),2),
    sum(SW_M6TO12),sum(M6TO12_DONE),
    ROUND(DECODE(SUM(NUM_DONE),0,NULL,SUM(M6TO12_DONE)*100/SUM(NUM_DONE)),2),
    ROUND(DECODE(SUM(SW_M6TO12),0,NULL,SUM(M6TO12_DONE)/SUM(SW_M6TO12)),2),
    sum(SW_M12TO24),sum(M12TO24_DONE),
    ROUND(DECODE(SUM(NUM_DONE),0,NULL,SUM(M12TO24_DONE)*100/SUM(NUM_DONE)),2),
    ROUND(DECODE(SUM(SW_M12TO24),0,NULL,SUM(M12TO24_DONE)/SUM(SW_M12TO24)),2),
    sum(SW_M24),sum(M24_DONE),
    ROUND(DECODE(SUM(NUM_DONE),0,NULL,SUM(M24_DONE)*100/SUM(NUM_DONE)),2),
    ROUND(DECODE(SUM(SW_M24),0,NULL,SUM(M24_DONE)/SUM(SW_M24)),2),
    SUM(NUM_DONE)
    from sql1
    where id in ({2})
    '''.format(sql1,  province, unit_list)
    cursor = connections['default'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': yy,
        'mm': mm,
        'yy1': yy1,
        'mm1': mm1,
        'yy2': yy2,
        'mm2': mm2,
        'opera': opera,
        'querys': querys
    }
    return render_to_response('bi_sales_rznxrjdctj.html', context, context_instance=RequestContext(request))


def wstat_swjbdctj(request, context):
    """
    描述：商务级别单产统计
    作者：凯伦kevin 2014年1月22日
    """
    EVENT_RIGHT = 1465
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    sql = u'''
     select aaa.unit,ccc.SHORT_DESCRIPTION,ccc.LEVEL_NAME,
   aaa.SW_lv0,bbb.lv0_DONE,
   ROUND(DECODE(bbb.NUM_DONE,0,NULL,bbb.lv0_DONE*100/bbb.NUM_DONE),2),
   ROUND(DECODE(aaa.SW_lv0,0,NULL,bbb.lv0_DONE/aaa.SW_lv0),2),
   aaa.SW_lv1,bbb.lv1_DONE,
   ROUND(DECODE(bbb.NUM_DONE,0,NULL,bbb.lv1_done*100/bbb.NUM_DONE),2),
   ROUND(DECODE(aaa.SW_lv1,0,NULL,bbb.lv1_done/aaa.SW_lv1),2),
   aaa.SW_lv2,bbb.lv2_DONE,
   ROUND(DECODE(bbb.NUM_DONE,0,NULL,bbb.lv2_done*100/bbb.NUM_DONE),2),
   ROUND(DECODE(aaa.SW_lv2,0,NULL,bbb.lv2_done/aaa.SW_lv2),2)
   FROM JGYJ_CUBE_VIEW bbb LEFT JOIN UNITS_PERSONS_CUBE_VIEW aaa
   ON aaa.UNIT = bbb.UNIT AND aaa.TIME = bbb.TIME
   LEFT JOIN UNIT_STATISTICS_VIEW ccc
   ON bbb.UNIT = ccc.dim_key
   WHERE bbb.TIME='M{0}CY{1}'
   AND ccc.LEVEL_NAME IN('UNIT','PROVINCE')
   AND ccc.SYSTEM='{2}'
   ORDER BY ccc.HIER_ORDER DESC
    '''.format(str.rjust(str(mm), 2, '0'), yy,settings.SYSTEM_KEY)
    cursor = connections['bi'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': yy,
        'mm': mm,
        'yy1': yy1,
        'mm1': mm1,
        'yy2': yy2,
        'mm2': mm2,
        'opera': opera,
        'querys': querys
    }
    return render_to_response('bi_sales_swjbdctj.html', context, context_instance=RequestContext(request))



def wstat_bmcpxsetj(request, context):
    """
    描述：部门产品销售额统计
    作者：凯伦kevin 2014年1月23日
    """
    EVENT_RIGHT = 1466
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    mm = int(request.GET.get('month', int(datetime.datetime.now().strftime('%m'))))
    de_id = int(request.GET.get('de_id', Mine.Depart.id))

    if str(mm) == '1':
        mm1 = 12
        yy1 = int(yy) - 1
    else:
        mm1 = int(mm) - 1
        yy1 = int(yy)

    if str(mm) == '12':
        mm2 = 1
        yy2 = int(yy) + 1
    else:
        mm2 = int(mm) + 1
        yy2 = int(yy)
    #部门下拉菜单
    depart_querys = Mine.get_depart()
    SelectDepartHTML = ''
    for q in depart_querys:
        SelectDepartHTML = SelectDepartHTML + '<option value="' + str(q.id) + '"'
        if str(de_id) == str(q.id):
            SelectDepartHTML = SelectDepartHTML + 'selected'
        SelectDepartHTML = SelectDepartHTML + '>'
        for y in range(1, q.depth):
            SelectDepartHTML = SelectDepartHTML + '│　'
        SelectDepartHTML = SelectDepartHTML + '├─'
        SelectDepartHTML = SelectDepartHTML + '[' + q.Unit.name.encode('utf-8') + ']' + q.name.encode('utf-8')
        SelectDepartHTML = SelectDepartHTML + '</option>'
    sql = u'''
    select aaa.product, aaa.depart, aaa.money,bbb.name as 产品名称, ccc.name as 部门名称
    from departs_products aaa
    inner join products_class bbb on aaa.product = bbb.id
    inner join departs ccc on aaa.depart = ccc.id
    where aaa.yyyy = {0} and aaa.mm = {1} and aaa.depart = {2}
     order by aaa.depart
    '''.format(yy, mm, de_id)
    cursor = connection.cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'opera': opera,
        'SelectDepartHTML': SelectDepartHTML,
        'querys': querys,
        'mm': mm,
        'yy': yy,
        'yy1': yy1,
        'mm1': mm1,
        'yy2': yy2,
        'mm2': mm2,
        'de_id': de_id
    }
    return render_to_response('bi_sales_bmcpxsetj.html', context, context_instance=RequestContext(request))


def wstat_bmqnyjtj(request, context):
    """
    描述：部门全年业绩统计
    作者：凯伦kevin 2014年1月23日
    """
    EVENT_RIGHT = 1467
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    year1 = str(yy-1)
    year2 = str(yy+1)

    if str(yy) == '2017':
        year2 = 2017
    departs_id = Mine.get_depart(format='ID_LIST')
    ids=",".join(["'{0}{1}'".format(settings.SYSTEM_KEY,id) for id in departs_id])
    sql = u'''
    select aaa.depart,bbb.name,aaa.yj from BMYJ aaa
    inner join departs bbb
    on aaa.depart = bbb.id
    where aaa.yyyy= {0} and aaa.depart in ({1})
    order by aaa.depart
    '''.format(yy, ids)
    cursor = connection.cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': yy,
        'year1': year1,
        'year2': year2,
        'opera': opera,
        'querys': querys
    }
    return render_to_response('bi_sales_bmqnyjtj.html', context, context_instance=RequestContext(request))


def wstat_bmgrqnyjtj(request, context):
    """
    描述：部门个人全年业绩统计
    作者：凯伦kevin 2014年1月23日
    """
    EVENT_RIGHT = 1468
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    yy = int(request.GET.get('year', int(datetime.datetime.now().strftime('%Y'))))
    year1 = str(yy-1)
    year2 = str(yy+1)

    if str(yy) == '2017':
        year2 = 2017
    de_id = int(request.GET.get('de_id', Mine.Depart.id))
    depart_querys = Mine.get_depart()
    SelectDepartHTML = ''
    for q in depart_querys:
        SelectDepartHTML = SelectDepartHTML + '<option value="' + str(q.id) + '"'
        if str(de_id) == str(q.id):
            SelectDepartHTML = SelectDepartHTML + 'selected'
        SelectDepartHTML = SelectDepartHTML + '>'
        for y in range(1, q.depth):
            SelectDepartHTML = SelectDepartHTML + '│　'
        SelectDepartHTML = SelectDepartHTML + '├─'
        SelectDepartHTML = SelectDepartHTML + '[' + q.Unit.name.encode('utf-8') + ']' + q.name.encode('utf-8')
        SelectDepartHTML = SelectDepartHTML + '</option>'
    sql = u'''
    select bbb.realname, aaa.单数完成 from (select account, sum(DSWC) as 单数完成 from sta_bestsales where yyyy = {0} group by account ) aaa
    inner join persons bbb
    on aaa.account = bbb.user_id
    where bbb.depart = {0}
    '''.format(de_id, yy,settings.SYSTEM_KEY)
    cursor = connection.cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'yy': yy,
        'year1': year1,
        'year2': year2,
        'opera': opera,
        'querys': querys,
        'SelectDepartHTML': SelectDepartHTML
    }
    return render_to_response('bi_sales_bmgrqnyjtj.html', context, context_instance=RequestContext(request))