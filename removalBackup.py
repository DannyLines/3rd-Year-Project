try:
    match_time_table_name = homeTeam.lower().replace("-", "_") + awayTeam.lower().replace("-", "_") + splitData[
        2] + "MatchTime"
    print("TRY EXCEPT")
    cursor.execute("select * from " + match_time_table_name)
    rows = cursor.fetchall()
    for row2 in rows:
        print(row2)
    time_exists = True
    true_time = browser2.find_element_by_id("part-top1")
    true_time = true_time.text[:2]
    print("TRUE TIME - " + str(true_time))
    if ((streamTweets.HOME_TEAM.lower() == homeTeam.lower()) and (
            streamTweets.AWAY_TEAM.lower() == awayTeam.lower())):
        try:
            create_table_string = "create table if not exists '" + match_time_table_name + "' (id INTEGER PRIMARY KEY, time TEXT)"
            cursor.execute(create_table_string)
            connection.commit()
        except Exception as e:
            print("table creation exception!")
            print(e)

        cursor.execute("DELETE FROM " + match_time_table_name)
        cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='" + match_time_table_name + "'")
        cursor.execute("INSERT INTO " + match_time_table_name + " (time) VALUES(?)", (true_time,))

        connection.commit()
except Exception as e:
    try:
        print("exception from tying to get time")
        # traceback.print_exc()
        print(e)

        true_time = browser2.find_element_by_id("part-top2")
        true_time = true_time.text
        print("TRUE TIME - " + str(true_time))

        if ((streamTweets.HOME_TEAM.lower() == homeTeam.lower()) and (
                streamTweets.AWAY_TEAM.lower() == awayTeam.lower())):
            create_table_string = "create table if not exists '" + match_time_table_name + "' (id INTEGER PRIMARY KEY, time TEXT)"
            cursor.execute(create_table_string)
            connection.commit()

            cursor.execute("DELETE FROM " + match_time_table_name)
            cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='" + match_time_table_name + "'")

            cursor.execute("INSERT INTO " + match_time_table_name + " (time) VALUES(?)", (true_time,))
            connection.commit()
    except:
        print("Neither first or 2nd half")
        time_exists = False
        try:
            print("IN TRY")
            try:
                print(match_time_table_name)
                create_table_string = "create table if not exists '" + match_time_table_name + "' (id INTEGER PRIMARY KEY, time TEXT)"
                cursor.execute(create_table_string)
                connection.commit()
                print("IN TRY NO ERROR")
            except Exception as e:
                print("in try error")
                print(e)
            cursor.execute("DELETE FROM " + match_time_table_name)
            cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='" + match_time_table_name + "'")
            connection.commit()

            print("MATCHTIME TEXT - " + str(matchTime))
            if matchTime[0].text.lower() == 'half time':
                print("HALF TIME ")
                cursor.execute("INSERT INTO " + match_time_table_name + " (time) VALUES(?)", ("45",))
                connection.commit()

            if (matchTime[0].text.lower() == 'finished'):
                print("match has finished!")
                try:
                    cursor.execute(
                        "INSERT INTO " + match_time_table_name + " (time) VALUES(?)", ("finished",))
                    connection.commit()
                except Exception as e:
                    print("Exception inserting 'finished' into the table")
                    print(e)
            else:
                true_time = "-1"
                cursor.execute("INSERT INTO " + match_time_table_name + " (time) VALUES(?)", (true_time,))
                connection.commit()
        except Exception as e:
            print("ANOTHER EXCEPTION HERE")
            traceback.print_exc()
            print(e)
            pass
        pass