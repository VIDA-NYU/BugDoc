import sys

def getColName(lst):
    return lst[0]

def isDataCol(name):
    if not (name == "p" or name == "id"):
        return name

def colLst(table,name):
    return table+"."+name+","

def decLst(name):
    return name[0]+" "+name[1]+","

def add(a,b):
    return a+b

def addVar(name):
    return [name, "varchar(64) default NULL"]

def addTxt(name):
    return [name, "text"]

def getSQL(table,which,select,frm,where,gby):
    if where == None:
        return "CREATE VIEW "+table+"_"+which+" AS SELECT "+select+" FROM "+frm+" GROUP BY "+gby
    else:
        return "CREATE VIEW "+table+"_"+which+" AS SELECT "+select+" FROM "+frm+" WHERE "+where+" GROUP BY "+gby

def exc(db,cur,sql):
    #
    try:
        cur.execute(sql)
        db.commit()
        return True
    except KeyboardInterrupt:
        exit()
    except:
        print(sql)
        print(sys.exc_info())
        print("\n\n")
        db.rollback()
        return False

