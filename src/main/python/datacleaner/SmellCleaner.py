import os
import shutil

from src.main.python.detector.DetectorStrategy import DetectorStrategy


import pandas as pd


class SmellCleaner:
    def __init__(self):
        pass


    def merge_files(self):
        design_cs = []
        path ="C:/workspace/MGL804_Projet/src\main/resources/data/smell/ant/"

        for file in os.listdir(path):
            fid, cs_type, commit = file.split('_')
            if file.endswith(".csv"):
                if cs_type=="designCodeSmells.":
                    print(file)
                    print(commit)
                    if len(design_cs) != 0:
                        new_file = pd.read_csv(path+file, header=0)
                        new_file['commit'] = commit
                        new_file['id_data'] = 0

                        last_id = len(design_cs.index.copy(deep=True))+1
                        new_last_id = len(new_file.index.copy(deep=True))+last_id

                        new_file['id_data'] = range(last_id, new_last_id)
                        new_file.set_index('id_data', inplace=True)

                        # new_file.set_index([pd.Index(range(last_id,new_last_id)), 'id_data'])
                        # new_file.set_index([pd.Index(range(last_id,new_last_id)), new_file.index])
                        # print(design_cs.index)

                        print(design_cs.index)
                        print(new_file.index)



                        frames = [design_cs, new_file]
                        result = pd.concat(frames)
                        design_cs=result.copy(True)
                        #
                        # design_cs = design_cs.join(new_file,
                        #                            how='outer',
                        #                            on='id_data'
                        #                            )

                        print("\n\n")
                    else:
                        design_cs =  pd.read_csv(path+file, header=0)
                        design_cs['commit'] = commit
                        design_cs['id_data'] = range(len(design_cs.index))
                        design_cs.set_index('id_data', inplace=True)
                        print(design_cs.index)

        design_cs.to_csv('__temp.csv',index=False)


        #             # remove some columns
        #             # new_file = new_file[new_file.columns.drop(list(new_file.filter(regex='^rsfx_.*$')))]
        #
        #         elif not os.path.exists(out_path):
        #             os.mkdir(out_path)
        #         new_file.to_csv(out_file_path, index=False)


SmellCleaner().merge_files()
