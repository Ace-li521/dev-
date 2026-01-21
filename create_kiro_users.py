#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiro 用户批量开通脚本
"""

import re
import boto3

IDENTITY_STORE_ID = 'd-90662c7920'
GROUP_NAME = 'Dev_AI'

client = boto3.client('identitystore')

# ============原始数据（从飞书表格复制到这里）============
RAW_DATA = """
wanglitao@itiger.com
"""

# 常用姓氏，用于解析姓名
COMMON_SURNAMES = [
    'gong', 'miao', 'yan', 'shen', 'yuan', 'ma', 'nangong', 'changsun',
    'zheng', 'zhang', 'huang', 'liang', 'cheng', 'deng', 'peng', 'jiang', 'qiao',
    'guan', 'xiao', 'dong', 'zhou', 'zhao', 'yang', 'wang', 'feng', 'tang', 'song',
    'han', 'cao', 'jin', 'qiu', 'yun', 'pan', 'lin', 'gao', 'liu', 'liao', 'yan',
    'luo', 'qin', 'cui', 'wei', 'shi', 'bai', 'kong', 'meng', 'xue', 'duan', 'lei',
    'hou', 'long', 'tao', 'wan', 'wen', 'fang', 'zou', 'xiong', 'mao', 'tan',
    'lu', 'gu', 'dai', 'ren', 'lv', 'yi', 'su', 'bo', 'du', 'fu', 'cai', 'lan','chen',
    'li', 'wu', 'xu', 'sun', 'hu', 'zhu', 'he', 'guo', 'ma', 'yu', 'ai', 'qu', 'chen', 'niu', 'mu', 'rong'
]


def extract_emails(raw_data):
    """从原始数据提取邮箱"""
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_data)
    # 去重
    return list(dict.fromkeys(emails))


def parse_name_from_email(email):
    """从邮箱解析用户名、姓、名"""
    username = email.split('@')[0].strip()
    base_name = re.sub(r'[0-9]+', '', username)  # 移除数字
    
    if len(base_name) < 2:
        return username, username, ""
    
    # 匹配姓氏
    for surname in COMMON_SURNAMES:
        if base_name.lower().startswith(surname.lower()):
            first_name = base_name[len(surname):]
            return username, first_name, surname
    
    # 默认：第一个字符是姓
    return username, base_name[1:], base_name[:1]


def get_group_id():
    """获取组 ID"""
    response = client.list_groups(
        IdentityStoreId=IDENTITY_STORE_ID,
        Filters=[{'AttributePath': 'DisplayName', 'AttributeValue': GROUP_NAME}]
    )
    return response['Groups'][0]['GroupId'] if response['Groups'] else None


def create_user(username, email, first_name, last_name):
    """创建用户"""
    try:
        response = client.create_user(
            IdentityStoreId=IDENTITY_STORE_ID,
            UserName=username,
            DisplayName=f"{first_name} {last_name}",
            Name={'GivenName': first_name, 'FamilyName': last_name},
            Emails=[{'Value': email, 'Primary': True}]
        )
        return response['UserId'], '创建成功'
    except client.exceptions.ConflictException:
        resp = client.list_users(
            IdentityStoreId=IDENTITY_STORE_ID,
            Filters=[{'AttributePath': 'UserName', 'AttributeValue': username}]
        )
        if resp['Users']:
            return resp['Users'][0]['UserId'], '已存在'
        return None, '已存在但获取ID失败'
    except Exception as e:
        return None, str(e)


def add_user_to_group(group_id, user_id):
    """将用户加入组"""
    try:
        client.create_group_membership(
            IdentityStoreId=IDENTITY_STORE_ID,
            GroupId=group_id,
            MemberId={'UserId': user_id}
        )
        return '已加入组'
    except client.exceptions.ConflictException:
        return '已在组中'
    except Exception as e:
        return f'加组失败: {e}'


def main():
    print("=" * 50)
    print("Kiro 用户批量开通脚本")
    print("=" * 50)
    
    # 1. 提取邮箱
    emails = extract_emails(RAW_DATA)
    if not emails:
        print("❌ 没有找到有效邮箱，请把数据粘贴到 RAW_DATA 变量中")
        return
    
    print(f"\n📧 提取到 {len(emails)} 个邮箱（已去重）")
    
    # 2. 获取组 ID
    group_id = get_group_id()
    if not group_id:
        print(f"❌ 找不到组 {GROUP_NAME}")
        return
    print(f"✅ 找到组 {GROUP_NAME}: {group_id}")
    
    # 3. 处理每个用户
    print(f"\n开始处理用户...")
    print("-" * 50)
    
    success_count = 0
    for email in emails:
        username, first_name, last_name = parse_name_from_email(email)
        
        # 创建用户
        user_id, user_msg = create_user(username, email, first_name, last_name)
        
        if user_id:
            # 加入组
            group_msg = add_user_to_group(group_id, user_id)
            print(f"✅ {username:<20} | {user_msg} | {group_msg}")
            success_count += 1
        else:
            print(f"❌ {username:<20} | {user_msg}")
    
    print("-" * 50)
    print(f"\n🎉 完成！成功处理 {success_count}/{len(emails)} 个用户")


if __name__ == '__main__':
    main()
