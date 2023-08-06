#---------- single sample:

from single_factor_model.single import preprocessing,back_testing,ic_measurement,ic_measure_summary,back_test_summary,bt_figure

parms={'factor_path':r'..\alpha_gen_factor'
      ,'ind_path':r'..\Industry'
      ,'ind_level':'level_name'
      ,'price_path':r'..\MktPrice'
      ,'cap_path':r'..\Cap'
      ,'index_weight_path':r'..\ZZ800_weight'
      ,'start_time':20170101
      ,'end_time':20180101
      ,'sub_factor':None
      ,'flag':'monthly'
      ,'day_lag':1
      ,'ind_mapping_flag':False
      }
parms2={'n':5
        ,'silent':True # whether to output detail
        } 
parms3={'window':3
        ,'half_decay':200
        } 
P=preprocessing()
D=P(**parms)
T=back_testing(D)
B=T(**parms2)
T2=ic_measurement(D)
M=T2(**parms3)

Table0=ic_measure_summary(M)
Dict1,Table2,Dict3=back_test_summary(B)
Dict4=bt_figure(B,show_plot=True)

Table0.to_csv(r'E:\table0.csv')

from RNWS import write
write.write_dict(Dict1,path='E:',file_pattern='dict1')

#---------- multi sample:

from single_factor_model.multi import preprocessing,back_testing,ic_measurement,ic_measure_summary,back_test_summary,bt_figure


parms={'factor_path':r'..\alpha_gen_factor'
      ,'ind_path':r'..\Industry_num'
      ,'ind_level':'level_name'
      ,'price_path':r'..\MktPrice'
      ,'cap_path':r'..\Cap'
      ,'index_weight_path':r'..\ZZ800_weight'
      ,'start_time':20170101
      ,'end_time':20180101
      ,'sub_factor':None
      ,'day_lag':1
      ,'flag':'monthly'
      ,'processors':3
      ,'ind_mapping_flag':False
      }
parms2={'n':5
        ,'silent':True
        ,'processors':3
        } 
parms3={'window':3
        ,'half_decay':200
        ,'processors':3
        }
if __name__=='__main__':
    P=preprocessing()
    D=P(**parms)
    T=back_testing(D)
    B=T(**parms2)
    T2=ic_measurement(D)
    M=T2(**parms3)
    Table0=ic_measure_summary(M)
    Dict1,Table2,Dict3=back_test_summary(B)
    Dict4=bt_figure(B,show_plot=True)

    Table0.to_csv(r'E:\table0.csv')
	from RNWS import write
    write.write_dict(Dict1,path='E:',file_pattern='dict1')