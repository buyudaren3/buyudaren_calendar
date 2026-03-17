#!/usr/bin/env python3
"""
生成包含中国农历节日和西方节日的 ICS 日历文件
"""

from datetime import datetime, timedelta, date
from zhdate import ZhDate
import uuid

def lunar_to_solar(year, month, day):
    """农历转公历"""
    try:
        zh = ZhDate(year, month, day)
        return zh.to_datetime().date()
    except:
        return None

def get_qingming_date(year):
    """计算清明节日期（21世纪公式）"""
    y = year - 2000
    day = int(4.81 + 0.242194 * y) - (y // 4)
    return day  # 返回4月的第几天

def get_nth_weekday(year, month, weekday, n):
    """获取某月第n个星期几 (weekday: 0=周一, 6=周日)"""
    from calendar import monthcalendar
    cal = monthcalendar(year, month)
    days = [week[weekday] for week in cal if week[weekday] != 0]
    return days[n - 1] if n <= len(days) else None

def generate_event(summary, start_date, uid_base, year=None):
    """生成单个事件"""
    end_date = start_date + timedelta(days=1)
    uid = f"{uid_base}{year if year else ''}"
    return f"""BEGIN:VEVENT
DTEND;VALUE=DATE:{end_date.strftime('%Y%m%d')}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART;VALUE=DATE:{start_date.strftime('%Y%m%d')}
SEQUENCE:0
SUMMARY:{summary}
UID:{uid}
END:VEVENT
"""

def generate_recurring_event(summary, month, day, uid_base, rrule=None):
    """生成重复事件"""
    start = datetime(2024, month, day).date()
    end = start + timedelta(days=1)
    rule = rrule or f"RRULE:FREQ=YEARLY;BYMONTH={month:02d};BYMONTHDAY={day:02d}"
    return f"""BEGIN:VEVENT
DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}
SEQUENCE:0
SUMMARY:{summary}
UID:{uid_base}
{rule}
END:VEVENT
"""

def generate_calendar():
    events = []
    current_year = datetime.now().year
    
    # 固定公历节日（每年重复）
    fixed_holidays = [
        ("元旦", 1, 1, "C1A2B3D4-E5F6-4789-ABCD-100000000001"),
        ("情人节", 2, 14, "B40484B8-EC47-423C-9FE2-ED8045510CD9"),
        ("妇女节", 3, 8, "C1A2B3D4-E5F6-4789-ABCD-100000000002"),
        ("植树节", 3, 12, "86B5610A-0ED1-45AA-AC5F-3986F5D0DCB3"),
        ("愚人节", 4, 1, "6CAE4024-D0F2-4644-B06C-1426082A5102"),
        ("劳动节", 5, 1, "C1A2B3D4-E5F6-4789-ABCD-100000000003"),
        ("青年节", 5, 4, "C1A2B3D4-E5F6-4789-ABCD-100000000004"),
        ("儿童节", 6, 1, "C1A2B3D4-E5F6-4789-ABCD-100000000005"),
        ("建党节", 7, 1, "C1A2B3D4-E5F6-4789-ABCD-100000000006"),
        ("建军节", 8, 1, "C1A2B3D4-E5F6-4789-ABCD-100000000007"),
        ("教师节", 9, 10, "AA61B842-5291-44AF-8084-1087FF739388"),
        ("国庆节", 10, 1, "C1A2B3D4-E5F6-4789-ABCD-100000000008"),
        ("万圣夜", 10, 31, "A6084884-0DC7-48B7-AA29-B2CFCF8167EA"),
        ("万圣节", 11, 1, "EE89587A-49B3-4F97-91AB-D667026AA81C"),
        ("平安夜", 12, 24, "448ADCB0-601C-4A25-A2BA-97C1ABB1BCEA"),
        ("圣诞节", 12, 25, "7FDD232F-7B79-4B80-B966-8881C2C3B943"),
    ]
    
    for name, month, day, uid in fixed_holidays:
        events.append(generate_recurring_event(name, month, day, uid))
    
    # 浮动公历节日
    # 母亲节：5月第2个周日
    events.append(generate_recurring_event("母亲节", 5, 12, "81B937BF-53A0-43C0-ADC1-562EB4CE7516", 
                                           "RRULE:FREQ=YEARLY;BYMONTH=5;BYDAY=2SU"))
    # 父亲节：6月第3个周日
    events.append(generate_recurring_event("父亲节", 6, 16, "ADFF064B-1DD7-4214-B362-F0D7386833FF",
                                           "RRULE:FREQ=YEARLY;BYMONTH=6;BYDAY=3SU"))
    # 感恩节：11月第4个周四
    events.append(generate_recurring_event("感恩节", 11, 28, "283FBA16-0DB1-49E5-9624-EA2DEA0C6C14",
                                           "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=4TH"))
    
    # 清明节（节气，逐年计算）
    for year in range(current_year, current_year + 5):
        qm_day = get_qingming_date(year)
        qm_date = date(year, 4, qm_day)
        events.append(generate_event("清明节", qm_date, "QINGMING-UID-BASE", year))

    # 农历节日（需要逐年计算）
    lunar_holidays = [
        ("腊八节", 12, 8, "BAA01739-384A-46E8-9938-2AA27831A94C"),
        ("北小年", 12, 23, "CE501CBA-DCFA-4026-AE7B-DB44148F8F7D"),
        ("南小年", 12, 24, "1CE501CBA-DCFA-4026-AE7B-DB44148F8F7D"),
        ("除夕", 12, 30, "CHUXI-2024-2030"),  # 注意：有的年份腊月只有29天
        ("春节", 1, 1, "CHUNJIE-2024-2030"),
        ("元宵节", 1, 15, "YUANXIAO-2024-2030"),
        ("龙抬头", 2, 2, "LONGTAITOU-2024-2030"),
        ("端午节", 5, 5, "DUANWU-2024-2030"),
        ("七夕", 7, 7, "QIXI-2024-2030"),
        ("中元节", 7, 15, "6715EF41-D73C-4687-8AD7-DA9546C8EEA3"),
        ("中秋节", 8, 15, "ZHONGQIU-2024-2030"),
        ("重阳节", 9, 9, "CHONGYANG-2024-2030"),
    ]
    
    for year in range(current_year, current_year + 5):
        for name, lunar_month, lunar_day, uid_base in lunar_holidays:
            # 农历腊月（12月）的节日在公历上位于下一年年初，
            # 即农历年Y的腊月 = 公历年Y+1，因此查公历year年的腊月节日需用农历year-1年
            lunar_year = year - 1 if lunar_month == 12 else year
            
            # 特殊处理除夕（可能是腊月29或30）
            if name == "除夕":
                # 先尝试腊月30
                solar_date = lunar_to_solar(lunar_year, 12, 30)
                if solar_date is None:
                    # 如果没有腊月30，用腊月29
                    solar_date = lunar_to_solar(lunar_year, 12, 29)
            else:
                solar_date = lunar_to_solar(lunar_year, lunar_month, lunar_day)
            
            if solar_date:
                events.append(generate_event(name, solar_date, uid_base, year))
    
    # 生成完整日历
    calendar = f"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
PRODID:-//Kui Calendar//Auto Generated//CN
VERSION:2.0
X-APPLE-CALENDAR-COLOR:#1BADF8
X-WR-CALNAME:捕鱼达人日历
{"".join(events)}END:VCALENDAR
"""
    return calendar

if __name__ == "__main__":
    calendar = generate_calendar()
    with open("buyudaren_calendar.ics", "w", encoding="utf-8") as f:
        f.write(calendar)
    print("日历已生成: buyudaren_calendar.ics")
