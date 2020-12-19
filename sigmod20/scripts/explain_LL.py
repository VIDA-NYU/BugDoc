import time
from helpers import *
from formulas import *
from functools import reduce

def run(table,rows,samplesize,db,cur):

    opt = '0'
    print("Table name=",table,"\nAlgorithm=","LL", "\nNumber of rows=", rows, "\nSample size=", samplesize, "\n")

    sql = 'select count(*) from '+table
    exc(db,cur,sql)
    tablesize = cur.fetchall()[0][0]
    diffthreshold=(int(tablesize)/5000) + 1 # ~0.02%

    sql = 'select * from '+table+' where 1>2'
    if not exc(db,cur,sql):
        exit()

    allcolumns = list(map(getColName,cur.description))
    columns = list(filter(isDataCol, allcolumns))

    #create summary table
    summary_cols = list(map(addVar, columns))
    summary_cols.append(["multiplier", "float default 0"])
    summary_cols.append(["samplemultiplier", "float default 0"])
    summary_cols.append(["gain", "float default 0"])
    summary_cols.append(["id", "serial"])
    summary_cols.append(["kl", "float default 'infinity'"])
    sql = "create table "+table+"_summary("+reduce(add,map(decLst,summary_cols)).rstrip(",")+")"
    drop = "drop table "+table+"_summary cascade"
    exc(db,cur,drop)
    exc(db,cur,sql)

    #create sample table
    sample_cols = list(map(addVar,columns))
    sample_cols.append(["id", "serial"])
    sample_cols.append(["p", "integer"])
    sql = "create table "+table+"_sample("+reduce(add,map(decLst,sample_cols)).rstrip(",")+")"
    sqltemp = "create table "+table+"_sample_temp("+reduce(add,map(decLst,sample_cols)).rstrip(",")+")"
    drop = "drop table "+table+"_sample cascade"
    droptemp = "drop table "+table+"_sample_temp cascade"
    exc(db,cur,drop)
    exc(db,cur,droptemp)
    exc(db,cur,sql)
    exc(db,cur,sqltemp)
    print('sql', sql)

    #create estimate view'
    dataCols =  list(map(lambda x: colLst(table,x).rstrip(","), columns))
    summCols =  list(map(lambda x: colLst(table+"_summary",x).rstrip(","), columns))

    def matchCl(dcol,scol):
        return " ("+scol+" IS NULL OR "+scol+" = "+dcol+") and"
    where = reduce(add,map(matchCl,dataCols,summCols)).rstrip("and")
    cLst = reduce(add,map(lambda x: colLst(table,x),allcolumns))
    gby = cLst.rstrip(",")
    select = cLst+"(2^(sum(multiplier)))/(2^(sum(multiplier))+1) as q"
    frm = table+","+table+"_summary"
    sql = getSQL(table,"estimate",select,frm,where,gby)

    exc(db,cur,sql)

    #create estimate ON SAMPLE view
    dataCols =  list(map(lambda x: colLst(table + "_sample",x).rstrip(","), columns))
    summCols =  list(map(lambda x: colLst(table+"_summary",x).rstrip(","), columns))
    def matchCl(dcol,scol):
        return " ("+scol+" IS NULL OR "+scol+" = "+dcol+") and"
    where = reduce(add,map(matchCl,dataCols,summCols)).rstrip("and")
    cLst = reduce(add,map(lambda x: colLst(table+"_sample",x),allcolumns))
    gby = cLst.rstrip(",")
    select = cLst+"(2^(sum(samplemultiplier)))/(2^(sum(samplemultiplier))+1) as q"
    frm = table+"_sample"+","+table+"_summary"
    sql = getSQL(table+"_sample","estimate",select,frm,where,gby)

    exc(db,cur,sql)

    #create max pats ON SAMPLE
    estCols =  list(map(lambda x: colLst(table+"_sample"+"_estimate",x).rstrip(","), columns))
    sampCols =  list(map(lambda x: colLst(table+"_sample",x).rstrip(","), columns))
    def nIf(col,ecol,scol):
        return " NULLIF("+ecol+",NULLIF("+ecol+","+scol+")) as o"+col+","
    select = reduce(add,map(nIf,columns,estCols,sampCols))+"count(*) as oct, sum("+table+"_sample_estimate.q) as sumq,sum("+table+"_sample_estimate.p) as sump"
    frm = table+"_sample"+"_estimate,"+table+"_sample"
    where = None #table+"_sample"+"_estimate.id != "+table+"_sample.id"
    gby = reduce(add,map(lambda x: "o"+x+",",columns)).rstrip(",")
    sql = getSQL(table+"_sample","maxpats",select,frm,where,gby)

    exc(db,cur,sql)

    #create datatuple type
    sql = "create type datatuple as ("+reduce(add,map(decLst,map(addTxt,columns))).rstrip(",")+")"
    drop = "drop type datatuple cascade"
    exc(db,cur,drop)
    exc(db,cur,sql)

    #create stored procedure
    sql = "create function subsets("+reduce(add,map(decLst,map(addTxt,columns)))+"opt integer)\n\treturns setof datatuple\nas $$\n\tdef rec(lst,i):\n\t\tif i == len(lst):\n\t\t\treturn [map(lambda x: None,lst)]\n\t\telse:\n\t\t\tret=[]\n\t\t\thalf = rec(lst,i+1)\n\t\t\tfor r in half:\n\t\t\t\tret.append(r)\n\t\t\t\tif not lst[i] == None:\n\t\t\t\t\tcr = r[:]\n\t\t\t\t\tcr[i]=lst[i]\n\t\t\t\t\tret.append(cr)\n\t\t\treturn ret\n\ttup  = ["+reduce(add,map(lambda x: x+",",columns)).rstrip(",")+"]\n\tif opt == 1:\n\t\tfor r in rec(tup,0):\n\t\t\tyield r\n\telse:\n\t\tyield tup\n$$ language plpythonu"
    exc(db,cur,sql)


    #create subsets view ON SAMPLE
    sql = "create view "+table+"_sample"+"_subsets as select subsets("+reduce(add,map(lambda x: "o"+x+",",columns))+opt+") as comp, oct, sump, sumq from "+table+"_sample"+"_maxpats"
    exc(db,cur,sql)


    #create agg pats ON SAMPLE
    select = reduce(add,map(lambda x: "(comp)."+x+" as "+x+",",columns))+"sum(oct) as ct, sum(sump) as p, sum(sumq) as q"
    frm = table+"_sample"+"_subsets"
    where = None
    gby = reduce(add,map(lambda x: x+",",columns)).rstrip(",")
    sql = getSQL(table+"_sample","aggpats",select,frm,where,gby)

    exc(db,cur,sql)



    # create corrected ON SAMPLE
    select = reduce(add,map(lambda x: "pat."+x+",",columns)) + "count(*), avg(samp.p) as avgp, avg(samp.q) as avgq, "+BSGainFormula+" AS gain, \
            CASE WHEN avg(samp.p)::numeric = avg(samp.q)::numeric THEN 0.0               \
                    WHEN avg(samp.p)::numeric = 0 THEN -9                                                        \
            ELSE  log(2::numeric,avg(samp.p)::numeric/avg(samp.q)::numeric)                                            \
            END  AS samplemultiplier"
    frm = table+"_sample_estimate samp,"+table+"_sample_aggpats pat"
    patCols =  map(lambda x: colLst("pat",x).rstrip(","), columns)
    sampCols =  map(lambda x: colLst("samp",x).rstrip(","), columns)
    where = reduce(add,map(matchCl,sampCols,patCols)).rstrip("and")
    gby =  reduce(add,map(lambda x: "pat."+x+",",columns)).rstrip(",") #+"ct,pat.p,q"
    sql = getSQL(table+"_sample","corrected",select,frm,where,gby)
    exc(db,cur,sql)


    # create rich summary view
    select = reduce(add,map(lambda x: "summ."+x+",",columns))+                \
    "summ.id,summ.multiplier,avg(p) as p, avg(q) as q, count(*) as ct,              \
    "+DiffFormula+" AS diff"
    frm = table+"_estimate est,"+table+"_summary summ"
    summCols =  map(lambda x: colLst("summ",x).rstrip(","), columns)
    estCols =  map(lambda x: colLst("est",x).rstrip(","), columns)
    where = reduce(add,map(matchCl,estCols,summCols)).rstrip("and")
    gby =  reduce(add,map(lambda x: "summ."+x+",",columns))+"summ.multiplier,summ.id"
    sql = getSQL(table,"richsummary",select,frm,where,gby)
    exc(db,cur,sql)

    # create rich summary view ON SAMPLE
    select = reduce(add,map(lambda x: "summ."+x+",",columns))+                \
    "summ.id,summ.samplemultiplier,avg(p) as p, avg(q) as q, count(*) as ct,              \
    "+DiffFormula+" AS diff"
    frm = table+"_sample_estimate est,"+table+"_summary summ"
    gby =  reduce(add,map(lambda x: "summ."+x+",",columns))+"summ.samplemultiplier,summ.id"
    sql = getSQL(table+"_sample","richsummary",select,frm,where,gby)
    exc(db,cur,sql)


    #create view kl
    sql = "CREATE VIEW "+table+"_kl as SELECT SUM( "+KLFormula+") FROM "+table+"_estimate"
    exc(db,cur,sql)

    #empty summary
    sql = 'delete from '+table+'_summary'

    #import pdb; pdb.set_trace() ### XXX BREAKPOINT
    exc(db,cur,sql)


    #top row in summary
    sql = 'insert into '+table+'_summary default values'
    exc(db,cur,sql)

    sql = 'delete from '+table+'_sample'
    exc(db,cur,sql)
    #Begin set seed
    sql ='select setseed(0)'
    exc(db,cur,sql)
    #End set seed

    tcquery = 0
    tsnsr =0
    tsample = 0
    tkl = 0
    t0=time.time()

    print("----------------------------------------------------\nExplanation table:")
    print("----------------------------------------------------")
    for i in range(rows):
        ts = time.time()


    #BEGIN get sample:
        ta=time.time()

        order = 'random()::numeric'

        sql = 'delete from '+table+'_sample_temp'
        exc(db,cur,sql)

        #get sample
        sql = 'insert into '+table+'_sample_temp select '+reduce(add,map(lambda x: x+",",columns))+'id,p from '+table+'_estimate order by '+order+' desc limit '+ samplesize
        exc(db,cur,sql)

        #empty sample
        sql = 'delete from '+table+'_sample'
        exc(db,cur,sql)
        sql = 'insert into '+table+'_sample select * from ' +table+'_sample_temp'
        exc(db,cur,sql)
        tsample= tsample + time.time() - ta
    #END get sample

    #BEGIN Sample Convergence Query:
        ta=time.time()
        while (True):
            #convergence query to set multiplier
            sql = "update "+table+"_summary set samplemultiplier = "+SampleMultiplierFormula+"FROM (select id,p,q from "+table+"_sample"+"_richsummary where diff > " + str(diffthreshold) + " order by diff desc limit 1) as t where t.id = "+table+"_summary.id"
            if not exc(db,cur,sql): break

            if cur.rowcount ==0:
                break
        tcquery= tcquery + time.time() - ta

    #Begin Select new summary row:
        ta=time.time()

        sql = "insert into "+table+"_summary("+reduce(add,map(lambda x:x+",",columns))+"samplemultiplier) select "+reduce(add,map(lambda x:x+",",columns))+"samplemultiplier from "+table+"_sample_corrected where gain > 1 order by gain desc limit 1"
        exc(db,cur,sql)

        tsnsr= tsnsr + time.time() - ta
    #End Select new summary row:

        sql = 'select * from '+table+'_summary order by id desc limit 1'
        exc(db,cur,sql)

        res = cur.fetchall()
        toprint=""
        for k in range(len(res[0]) - 4):
            j=res[0][k]
            if str(j) == 'None':
                toprint+="*,"
            else:
                toprint+=str(j)+","

        print("Pattern",i+1,":",toprint.rstrip(','))

    t1= time.time()


    #Begin KL:
    ta=time.time()
    while (True):
        #convergence query to set multiplier
        sql = "update "+table+"_summary SET multiplier = "+MultiplierFormula+" FROM (select id,p,q from "+table+"_richsummary where diff > " + str(diffthreshold) + " order by diff desc limit 1) as t where t.id = "+table+"_summary.id"
        if not exc(db, cur, sql): break

        if cur.rowcount ==0:
            break

    sql = 'select * from '+table+'_kl'

    exc(db,cur,sql)
    kl = cur.fetchall()[0][0]
    print("----------------------------------------------------")
    print("Kullback Leibler divergence:",kl)
    print("----------------------------------------------------")

    tkl= time.time() - ta

    db.commit()

