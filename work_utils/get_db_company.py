import pymysql


# 1.连接到mysql数据库
def get_keyword():

    conn = pymysql.connect(host='***', port=3306, user='root', password='axy#mysql2019',
                           db='peng', charset="utf8", use_unicode=True)
    cursor = conn.cursor()
    sql = 'select name from district'
    cursor.execute(sql)
    all_key = cursor.fetchall()
    cursor.close()
    conn.close()
    return all_key


if __name__ == '__main__':
    all_key = get_keyword()
    for key_word in all_key:
        word = key_word[0]
        key_words = word[0:2]
        print(key_words)
