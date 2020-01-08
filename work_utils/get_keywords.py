import pymysql


# 1.连接到mysql数据库
def get_keywords():
    conn = pymysql.connect(host='***', port=3306, user='root', password='axy#mysql2019',
                           db='shihe_data', charset="utf8", use_unicode=True)
    cursor = conn.cursor()
    sql = 'select key_word from Surname ORDER BY id'
    sql2 = 'select name from Chinese_characters'
    cursor.execute(sql)
    key_xing = cursor.fetchall()
    cursor.execute(sql2)
    key_word = cursor.fetchall()
    cursor.close()
    conn.close()
    return key_xing, key_word


if __name__ == '__main__':
    sur_tuple, key_words_tuple = get_keywords()
    for keyword in key_words_tuple:
        # with open('key.txt', 'a', encoding='utf-8') as f:
        #     f.write(keyword[0])
        for sur in sur_tuple:
            sur_str = sur[0]
            key_words = sur_str[0:1] + keyword[0]
            print(key_words)
