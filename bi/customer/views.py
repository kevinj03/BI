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


def wstat_khshtj(request, context):
    """
    描述：客户审核情况统计
    作者：凯伦kevin 2014年2月25日
    """
    EVENT_RIGHT = 1459
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
   select a.UNIT,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.APPROVE,a.REFUSE,a.PTLR,a.SJZDR,a.SUM,a.SHTGL
   from KHSH_CUBE_VIEW a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT = b.DIM_KEY
   WHERE a.TIME = 'M{0}CY{1}'
    AND b.LEVEL_NAME IN ('UNIT','PROVINCE')
    AND b.SYSTEM='{2}'
    ORDER BY b.HIER_ORDER DESC
    '''.format(str.rjust(str(mm), 2, '0'), yy, settings.SYSTEM_KEY)
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
    return render_to_response('bi_customer_khshtj.html', context, context_instance=RequestContext(request))


def wstat_xsztgm(request, context):
    """
    描述：线索状态更名统计
    作者：凯伦kevin 2014年2月25日
    """
    EVENT_RIGHT = 1460
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
    select a.UNIT,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.APPROVE,a.REFUSE,a.SUM
   from XSZTGM_CUBE_VIEW a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT = b.DIM_KEY
   WHERE a.TIME = 'M{0}CY{1}'
    AND b.LEVEL_NAME IN ('UNIT','PROVINCE')
    AND b.SYSTEM='{2}'
    ORDER BY b.HIER_ORDER DESC
    '''.format(str.rjust(str(mm), 2, '0'), yy, settings.SYSTEM_KEY)
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
    return render_to_response('bi_customer_xsztgm.html', context, context_instance=RequestContext(request))


def wstat_hmdtj(request, context):
    """
    描述：黑名单统计
    作者：凯伦kevin 2014年2月25日
    """
    EVENT_RIGHT = 1469
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
    select a.UNIT,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.APPLICATION,a.DELETEKH,a.RECOVER,a.UNTREATED
   from BLACKLIST_CUBE_VIEW a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT = b.DIM_KEY
   WHERE a.TIME = 'M{0}CY{1}'
    AND b.LEVEL_NAME IN ('UNIT','PROVINCE')
    AND b.SYSTEM='{2}'
    ORDER BY b.HIER_ORDER DESC
    '''.format(str.rjust(str(mm), 2, '0'), yy, settings.SYSTEM_KEY)
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
    return render_to_response('bi_customer_hmdtj.html', context, context_instance=RequestContext(request))


def wstat_dqxzh(request, context):
    """
    描述：待清洗转回数量统计
    作者：凯伦kevin 2014年2月25日
    """
    EVENT_RIGHT = 1470
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
   select a.UNIT,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.APPROVE,a.REFUSE,a.SUM
   from DQXZH_CUBE_VIEW a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT = b.DIM_KEY
   WHERE a.TIME = 'M{0}CY{1}'
    AND b.LEVEL_NAME IN ('UNIT','PROVINCE')
    AND b.SYSTEM='{2}'
    ORDER BY b.HIER_ORDER DESC
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
    return render_to_response('bi_customer_dqxzhsl.html', context, context_instance=RequestContext(request))


def wstat_jjlryy(request, context):
    """
    描述：录入拒绝原因统计
    作者：凯伦kevin 2014年2月26日
    """
    EVENT_RIGHT = 1471
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
    select a.UNIT,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.ZLBWZ,a.YCZ,a.DHCT,a.WJT,a.JTBWZ,a.LRJTBF,a.GSMCGSCW,a.HYBSH,
    a.GSLXGXCW,a.YSDHGSCW,a.GSDZBHG,a.OTHER
   from LRJJYY_CUBE_VIEW a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT = b.DIM_KEY
   WHERE a.TIME = 'M{0}CY{1}'
    AND b.LEVEL_NAME IN ('UNIT','PROVINCE')
    AND b.SYSTEM='{2}'
    ORDER BY b.HIER_ORDER DESC
    '''.format(str.rjust(str(mm), 2, '0'), yy, settings.SYSTEM_KEY)
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
    return render_to_response('bi_customer_jjlryy.html', context, context_instance=RequestContext(request))


def wstat_wshzy(request, context):
    """
    描述：未审核资源统计
    作者：凯伦kevin 2014年2月26日
    """
    EVENT_RIGHT = 1472
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    stime = request.GET.get('sTime', datetime.datetime.now().strftime('%Y-%m-%d'))
    unlist=Mine.get_unit(format='ID_LIST')
    unliststr=""
    for id in unlist:
        unliststr=unliststr+"'"+settings.SYSTEM_KEY+str(id)+"',"
    unliststr=unliststr[:-1]
    sql = u'''
    select a.UNIT_KEY,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.PUBLIC_THREAD,a.PTGJ,a.QYGJ,a.QYLKH,
    (a.PUBLIC_THREAD+a.PTGJ+a.QYGJ+a.QYLKH) AS SUM
   from WSHZY_FACT a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT_KEY = b.DIM_KEY
   WHERE a.DAY_KEY = to_date('{0}','yyyy-mm-dd')
    AND b.DIM_KEY in ({1})
    ORDER BY b.HIER_ORDER,a.DAY_KEY DESC
    '''.format(stime, unliststr)
    print sql
    cursor = connections['bi'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'sTime': stime,
        'opera': opera,
        'querys': querys
    }
    return render_to_response('bi_customer_wshzy.html', context, context_instance=RequestContext(request))


def wstat_bmxslr(request, context):
    """
    描述：部门线索录入统计
    作者：凯伦kevin 2014年2月26日
    """
    EVENT_RIGHT = 1473
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
    departs_id = Mine.get_depart(format='ID_LIST')
    ids = ",".join(["'{0}{1}'".format(settings.SYSTEM_KEY, id) for id in departs_id])

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
    select a.DEPART,b.depart_name,b.depth,a.APPROVE,a.REFUSE，a.SUM
    from BMXSLR_CUBE_VIEW a
    INNER JOIN dim_departs b
    ON a.DEPART=b.depart_key
    WHERE a.TIME='M{0}CY{1}'
    and a.depart in ({2})
    ORDER BY b.orders
    '''.format(str.rjust(str(mm), 2, '0'), yy, ids)
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
    return render_to_response('bi_customer_bmxslr.html', context, context_instance=RequestContext(request))


def wstat_xszttj(request, context):
    """
    描述：线索状态统计
    作者：凯伦kevin 2014年2月26日
    """
    EVENT_RIGHT = 1475
    try:
        Mine = request.session['mine_object']
        Mine.reload()
    except Exception, e:
        Mine = MineManager()
    opera = Mine.auth(EVENT_RIGHT)
    if type(opera) == type(''):
        return HttpResponse(opera)
    stime = request.GET.get('sTime', datetime.datetime.now().strftime('%Y-%m-%d'))
    unlist=Mine.get_unit(format='ID_LIST')
    unliststr=""
    for id in unlist:
        unliststr=unliststr+"'"+settings.SYSTEM_KEY+str(id)+"',"
    unliststr=unliststr[:-1]
    sql = u'''
    select a.UNIT_KEY,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.XS,a.BLACKXS,a.YGJ,a.BIGCUSTOMER，a.CUSTOMER,
   a.BLACKCUSTOMER,a.DQX
   from XS_STATUS_FACT a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT_KEY = b.DIM_KEY
   WHERE a.DAY_KEY =to_date('{0}','yyyy-mm-dd')
    AND b.DIM_KEY in ({1})
    ORDER BY b.HIER_ORDER,a.DAY_KEY DESC
    '''.format(stime,unliststr)
    cursor = connections['bi'].cursor()
    cursor.execute(sql)
    querys = cursor.fetchall()
    cursor.close()
    connection.close()
    context = {
        'opera': opera,
        'querys': querys,
        'sTime': stime,
    }
    return render_to_response('bi_customer_xszttj.html', context, context_instance=RequestContext(request))


def wstat_lkhgm(request, context):
    """
    描述：老客户更名统计
    作者：凯伦kevin 2014年2月26日
    """
    EVENT_RIGHT = 1476
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
    select a.UNIT,b.SHORT_DESCRIPTION,b.LEVEL_NAME,a.GMSL
   from LKHGM_CUBE_VIEW a LEFT JOIN UNIT_STATISTICS_VIEW b
   ON a.UNIT = b.DIM_KEY
   WHERE a.TIME = 'M{0}CY{1}'
    AND b.LEVEL_NAME IN ('UNIT','PROVINCE')
    AND b.SYSTEM='{2}'
    ORDER BY b.HIER_ORDER DESC
    '''.format(str.rjust(str(mm), 2, '0'), yy, settings.SYSTEM_KEY)
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
    return render_to_response('bi_customer_lkhgm.html', context, context_instance=RequestContext(request))








