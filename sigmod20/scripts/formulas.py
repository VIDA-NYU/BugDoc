
MultiplierFormula=" CASE WHEN p::numeric = q::numeric THEN multiplier                                                          \
        WHEN p::numeric = 0.0 THEN multiplier - 9                                                                                           \
        WHEN q::numeric = 1.0 THEN multiplier - 9                                                                                           \
        WHEN p::numeric = 1.0 THEN multiplier + 9                                                                                          \
        WHEN q::numeric = 0.0 THEN multiplier + 9                                                                                          \
        ELSE multiplier + log(2::numeric, p::numeric/q::numeric) + log(2::numeric, (1-q::numeric)/(1-p::numeric)) \
        END "

SampleMultiplierFormula=" CASE WHEN p::numeric = q::numeric THEN samplemultiplier                                               \
        WHEN p::numeric = 0.0 THEN samplemultiplier - 9                                                                                           \
        WHEN q::numeric = 1.0 THEN samplemultiplier - 9                                                                                           \
        WHEN p::numeric = 1.0 THEN samplemultiplier + 9                                                                                          \
        WHEN q::numeric = 0.0 THEN samplemultiplier + 9                                                                                          \
        ELSE samplemultiplier + log(2::numeric, p::numeric/q::numeric) + log(2::numeric, (1-q::numeric)/(1-p::numeric)) \
        END "


DiffFormula = " CASE WHEN avg(p)::numeric = avg(q)::numeric THEN 0.0 \
WHEN (avg(p)::numeric = 0.0 and avg(q)::numeric = 1.0) THEN count(*) \
WHEN avg(p)::numeric = 0.0 THEN (count(*)::numeric) * log(2::numeric, 1.0/(1.0-avg(q)::numeric)::numeric) \
WHEN (avg(p)::numeric = 1.0 AND avg(q)::numeric = 0.0) THEN (count(*)::numeric) \
WHEN avg(p)::numeric = 1.0 THEN (count(*)::numeric) * log(2::numeric, 1.0/avg(q)::numeric) \
WHEN avg(q)::numeric = 0.0 THEN (count(*)::numeric)*(avg(p)::numeric)* 9 + (count(*)::numeric)*(1-avg(p)::numeric)*log(2::numeric, (1-avg(p)::numeric)) \
WHEN avg(q)::numeric = 1.0 THEN (count(*)::numeric)*(avg(p)::numeric)*log(2::numeric, avg(p)::numeric) + (count(*)::numeric)*(1-avg(p)::numeric) * 9 \
ELSE (count(*)::numeric)*(avg(p)::numeric)*log(2::numeric, avg(p)::numeric/avg(q)::numeric) + (count(*)::numeric)*(1-avg(p)::numeric)*log(2::numeric, (1-avg(p)::numeric)/(1-avg(q)::numeric)::numeric) \
END "

smartDiffFormula = " CASE \
WHEN sum(sump) = sum(sumq) \
        THEN 0.0 \
WHEN (sum(sump) = 0 AND sum(sumq) = sum(support)) \
        THEN sum(support) \
WHEN sum(sump) = 0 \
        THEN (sum(support)::numeric) * log(2::numeric,sum(support)/(sum(support) -sum(sump)::numeric)::numeric) \
WHEN (sum(sump) = sum(support) AND sum(sumq) = 0) \
        THEN sum(support) \
WHEN sum(sump) = sum(support) \
        THEN sum(support) * log(2::numeric, sum(support) /sum(sumq)::numeric) \
WHEN sum(sumq) = 0 \
        THEN (sum(sump) * 9 ) + ((sum(support)-sum(sump))*log(2::numeric, (1-(sum(sump)/sum(support)::numeric)::numeric)) )\
WHEN sum(sumq) = sum(support) \
        THEN (sum(sump)*log(2::numeric, sum(sump)/sum(support)::numeric) ) +\
             ((sum(support)- sum(sump) ) * 9 )\
        ELSE (sum(sump)::numeric*log(2::numeric, sum(sump)::numeric/sum(sumq)::numeric))\
        +((sum(support)-sum(sump))*log(2::numeric, (sum(support)-sum(sump))/(sum(support)-sum(sumq))::numeric)) \
END "

GainFormula = "CASE WHEN pat.p/ct::numeric = q/ct THEN 0.0                                                                                                            \
                 WHEN pat.p/ct::numeric = 0.0 THEN (ct/count(*))*(1-pat.p)*log(2::numeric,(ct-pat.p)/(ct-q::numeric)::numeric)  \
                 WHEN pat.p/ct::numeric = 1.0 THEN (ct/count(*)::numeric)*(pat.p/ct::numeric)*log(2::numeric,pat.p/q::numeric)                 \
          ELSE  ((ct/count(*)::numeric)*(1-pat.p/ct::numeric)*log(2::numeric, (ct-pat.p)/(ct-q)::numeric) )+                                          \
                ((ct/count(*)::numeric)*(pat.p/ct::numeric)*log(2::numeric,pat.p/q::numeric))        \
          END "

SimpleFormula = "CASE WHEN sum(p) = sum(q) THEN 0.0     \
          WHEN sum(p) = 0.0 THEN sum(oct)*log(2::numeric,sum(oct)::numeric/(sum(oct)-sum(q))::numeric)    \
          WHEN sum(p) = sum(oct) THEN sum(p)*log(2::numeric,sum(p)::numeric/sum(q)::numeric)   \
          ELSE  ((( sum(oct) - sum(p)) * log(2::numeric, ( sum(oct) - sum(p))::numeric / ( sum(oct)- sum(q))::numeric)) + \
                ((sum(p))*log(2::numeric, sum(p)::numeric/sum(q)::numeric)) ) \
          END "

PS_GainFormula = "CASE WHEN avg(p) = avg(q) THEN 0.0                                                                                                            \
        WHEN avg(p)::numeric = 0.0 THEN (count(*))*log(2::numeric,(1::numeric)/(1-avg(q)::numeric)::numeric)  \
        WHEN avg(p)::numeric = 1.0 THEN (count(*))*log(2::numeric,1::numeric/avg(q)::numeric)                 \
        ELSE    (sum(p)::numeric*log(2::numeric, (avg(p)/avg(q)::numeric))) +   \
                ((count(*)::numeric - sum(p))*log(2::numeric,(1-avg(p)::numeric)/(1-avg(q)::numeric)))        \
        END "
def LLGainFormula(table):
    return "CASE WHEN avg("+table+"_sample_estimate.p)= avg("+table+"_sample_estimate.q) THEN 0.0                                                                                                    \
                 WHEN avg("+table+"_sample_estimate.p)::numeric = 0.0 THEN (count(*)::numeric)*log(2::numeric,1/(1-avg("+table+"_sample_estimate.q))::numeric)::numeric      \
                 WHEN avg("+table+"_sample_estimate.p)::numeric = 1.0 THEN (count(*)::numeric)*log(2::numeric,1/avg("+table+"_sample_estimate.q)::numeric)::numeric            \
            ELSE  ((count(*)::numeric)*avg("+table+"_sample_estimate.p)::numeric*log(2::numeric, avg("+table+"_sample_estimate.p)::numeric/avg("+table+"_sample_estimate.q)::numeric)::numeric )+ \
                   ((count(*)::numeric)*(1-avg("+table+"_sample_estimate.p)::numeric)* log(2::numeric,(1-avg("+table+"_sample_estimate.p)::numeric)/(1-avg("+table+"_sample_estimate.q)::numeric) ))    \
            END "
LLDCBtoDBGainFormula= "CASE WHEN avg(DB.p)= avg(DB.q) THEN 0.0                                                                                                    \
                 WHEN avg(DB.p)::numeric = 0.0 THEN (count(*)::numeric)*log(2::numeric,1/(1-avg(DB.q))::numeric)::numeric      \
                 WHEN avg(DB.p)::numeric = 1.0 THEN (count(*)::numeric)*log(2::numeric,1/avg(DB.q)::numeric)::numeric          \
            ELSE  ((count(*)::numeric)*avg(DB.p)::numeric*log(2::numeric, avg(DB.p)::numeric/avg(DB.q)::numeric)::numeric ) +  \
                   ((count(*)::numeric)*(1-avg(DB.p)::numeric)* log(2::numeric,(1-avg(DB.p)::numeric)/(1-avg(DB.q)::numeric) ))    \
            END "

Classic_GainFormula = "CASE WHEN avg(p) = avg(q) THEN 0.0                                                   \
        WHEN avg(p)::numeric = 0.0 THEN count(*)*log(2::numeric,(1::numeric)/(1-avg(q)::numeric)::numeric)   \
        WHEN avg(p)::numeric = 1.0 THEN count(*)*log(2::numeric, 1::numeric/avg(q)::numeric)           \
        ELSE    (((count(*)::numeric)-(sum(p)::numeric))*log(2::numeric, (1.0-avg(p)::numeric)/(1.0-avg(q))::numeric)) +           \
                ((sum(p)::numeric)*log(2::numeric,avg(p)::numeric/avg(q)::numeric))                               \
        END "


BSGainFormula = "CASE WHEN avg(samp.p)= avg(samp.q) THEN 0.0                                                                                                    \
                 WHEN avg(samp.p)::numeric = 0.0 THEN (count(*)::numeric)*log(2::numeric,1/(1-avg(samp.q))::numeric)::numeric      \
                 WHEN avg(samp.p)::numeric = 1.0 THEN (count(*)::numeric)*log(2::numeric,1/avg(samp.q)::numeric)::numeric            \
          ELSE  ((count(*)::numeric)*avg(samp.p)::numeric*log(2::numeric, avg(samp.p)::numeric/avg(samp.q)::numeric)::numeric )+ \
                   ((count(*)::numeric)*(1-avg(samp.p)::numeric)* log(2::numeric,(1-avg(samp.p)::numeric)/(1-avg(samp.q)::numeric) ))    \
          END "


KLFormula = " CASE WHEN p::numeric = q::numeric THEN 0.0 		        	\
		WHEN p::numeric = 1.0 AND q::numeric = 0.0 THEN 9				\
		WHEN p::numeric = 1.0 THEN - log(2::numeric, q::numeric) 		        \
		WHEN p::numeric = 0.0 AND q::numeric = 1.0 THEN 9 				\
		WHEN p::numeric = 0.0 THEN - log(2::numeric,(1-q::numeric)) 	        \
		ELSE 9 END "


