import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler,MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer


from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    #Get the preprocessor pkl file location
    preprocessor_obj_file_path=os.path.join("artifacts",'preprocessor.pkl')


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self):
        ###For uploading the preprocessing pickle file into the artifacts folder
        try:
            numerical_columns = ['writing_score','reading_score']
            categorical_columns = ['gender','race_ethnicity','parental_level_of_education','lunch','test_preparation_course']
            #lr = LinearRegression()
             
            #SimpleImputer(strategy='median')
            num_pipeline=Pipeline(
                steps=[
                    ('imputer',IterativeImputer(
                        estimator = LinearRegression(),
                        max_iter = 10,
                        tol = 1e-10,
                        imputation_order = 'roman',
                            )),
                    ('scaler',StandardScaler())
                    ]
            )

            cat_pipeline=Pipeline(steps = [
                    ('imputer',SimpleImputer(strategy='most_frequent')),
                     ('one_hot_encoder',OneHotEncoder()),
                    ])
            

            
            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")

   
            preprocessor=ColumnTransformer(
                [
                ("num_pipeline",num_pipeline,numerical_columns),
                ("cat_pipelines",cat_pipeline,categorical_columns)]


            )


            return preprocessor

        except Exception as e:
            raise CustomException(e,sys)

        
        


    def initiate_data_transformation(self,train_path,test_path):
        '''the train and test path will be received from dataingestion'''
        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("Train and Test data read")

            preprocessing_obj = self.get_data_transformer_object()

            target_column_name = "math_score"
            #numerical_columns = ['writing_score','reading_score']

            ##Filtering for the independent variables

            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)

             ## Filtering for the target variable/depdent variable

            target_feature_train_df=train_df[target_column_name]


            input_feature_test_df=test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df=test_df[target_column_name]


            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe. Making sure to collect the array outputs"
            )



            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[
                input_feature_train_arr, np.array(target_feature_train_df)
            ]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info(f"Saving preprocessing object.")

            save_object(

                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj

            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )


        except Exception as e:
            raise CustomException(e,sys)




