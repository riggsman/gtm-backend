import pymysql


class SqlHelper:
    def create_user_and_grant_privileges(username, password, database_name):
        root_user = "root"
        # root_password= ""
        port=3306
        host="localhost"

        conn = pymysql.connect(
            host=host,
            user=root_user,
            port=port,
            autocommit=True
        )

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
                cursor.execute(
                    f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{password}';"
                )
                
                cursor.execute(
                    f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'%';"
                )
                cursor.execute(
                    f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'localhost';"
                )
                cursor.execute(
                    f"GRANT SELECT, INSERT, UPDATE, DELETE ON {database_name}.* TO '{username}'@'%';"
                )
                
                cursor.execute(
                    "FLUSH PRIVILEGES;"
                )
                cursor.execute(
                    f"SELECT Host, User FROM mysql.user WHERE User = 'tgmi';"
                )
                cursor.execute(
                    f"SHOW GRANTS FOR 'tgmi'@'localhost';"
                )
                

              
                print(f"USER {username} CREATED SUCCESSFULLY WITH ALL PRIVILEGES")
        finally:
            conn.close()
