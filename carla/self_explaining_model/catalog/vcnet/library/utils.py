# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_data.ipynb (unless otherwise specified).

__all__ = ['dict2json', 'load_json', 'update_json_file', 'bn_func', 'x1_to_x3', 'x1x2_to_x4', 'bn_gen',
           'load_adult_income_dataset', 'load_learning_analytic_data', 'NumpyDataset', 'PandasDataset', 'uniform',
           'hinge_loss', 'cat_normalize', 'l1_mean', 'get_loss_functions', 'get_optimizers', 'smooth_y']

# Cell
from import_essentials import *



def fix_seed(seed=42) : 
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


# Cell
def dict2json(dictionary: dict, file_name: str):
    with open(file_name, "w") as outfile:
        json.dump(dictionary, outfile, indent = 4)

def load_json(file_name: str):
    with open(file_name) as json_file:
        return json.load(json_file)

def update_json_file(param: dict, file_name: str):
    if os.path.exists(file_name):
        old_param = load_json(file_name)
    else:
        old_param = {}
    # copy to old_param
    for k in param.keys():
        old_param[k] = param[k]
    dict2json(old_param, file_name)
    return old_param

# Cell
def bn_func(x1, x2, x3, x4):
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
    return sigmoid(10.5 * ((x1 * x2) / 8100) + 10 - np.random.normal(1, 0.1, 10000) * x3 + 1e-3 * x4)

def x1_to_x3(x1):
    return 1/3 * x1 - 5

def x1x2_to_x4(x1, x2):
    return x1 * np.log(x2 **2) / 10 - 10

def bn_gen():
    """
    modify code from: https://github.com/divyat09/cf-feasibility/blob/master/generativecf/scripts/simple-bn-gen.py
    """
    x1 = np.random.normal(50, 15, 10000)
    x2 = np.random.normal(35, 17, 10000)
    x3 = x1_to_x3(x1) + np.random.normal(0, 1, 10000)
    x4 = x1x2_to_x4(x1, x2) + np.random.normal(0, 1, 10000)
    y= bn_func(x1, x2, x3, x4)

    data = np.zeros((x1.shape[0], 5))
    data[:, 0] = x1
    data[:, 1] = x2
    data[:, 2] = x3
    data[:, 3] = x4
    data[:, 4] = np.array(y > .5, dtype=np.int)

    return pd.DataFrame(data, columns=['x1', 'x2', 'x3', 'x4', 'y'])

# Cell

def load_adult_income_dataset(path=None):
    """Loads adult income dataset from https://archive.ics.uci.edu/ml/datasets/Adult and prepares the data for data analysis based on https://rpubs.com/H_Zhu/235617
    :return adult_data: returns preprocessed adult income dataset.
    copy from https://github.com/interpretml/DiCE/blob/master/dice_ml/utils/helpers.py
    """
    if path is None:
        raw_data = np.genfromtxt(
            'https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data',
            delimiter=', ',
            dtype=str
        )
    else:
        raw_data = np.genfromtxt(
            path,
            delimiter=', ',
            dtype=str
        )

    #  column names from "https://archive.ics.uci.edu/ml/datasets/Adult"
    column_names = ['age', 'workclass', 'fnlwgt', 'education', 'educational-num',
                    'marital-status', 'occupation', 'relationship', 'race', 'gender',
                    'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income']

    adult_data = pd.DataFrame(raw_data, columns=column_names)

    # For more details on how the below transformations are made, please refer to https://rpubs.com/H_Zhu/235617
    adult_data = adult_data.astype(
        {"age": np.int64, "educational-num": np.int64, "hours-per-week": np.int64})

    adult_data = adult_data.replace(
        {'workclass': {'Without-pay': 'Other/Unknown', 'Never-worked': 'Other/Unknown'}})
    adult_data = adult_data.replace({'workclass': {
                                    'Federal-gov': 'Government', 'State-gov': 'Government', 'Local-gov': 'Government'}})
    adult_data = adult_data.replace(
        {'workclass': {'Self-emp-not-inc': 'Self-Employed', 'Self-emp-inc': 'Self-Employed'}})
    adult_data = adult_data.replace(
        {'workclass': {'Never-worked': 'Self-Employed', 'Without-pay': 'Self-Employed'}})
    adult_data = adult_data.replace({'workclass': {'?': 'Other/Unknown'}})

    adult_data = adult_data.replace({'occupation': {'Adm-clerical': 'White-Collar', 'Craft-repair': 'Blue-Collar',
                                                    'Exec-managerial': 'White-Collar', 'Farming-fishing': 'Blue-Collar',
                                                    'Handlers-cleaners': 'Blue-Collar',
                                                    'Machine-op-inspct': 'Blue-Collar', 'Other-service': 'Service',
                                                    'Priv-house-serv': 'Service',
                                                    'Prof-specialty': 'Professional', 'Protective-serv': 'Service',
                                                    'Tech-support': 'Service',
                                                    'Transport-moving': 'Blue-Collar', 'Unknown': 'Other/Unknown',
                                                    'Armed-Forces': 'Other/Unknown', '?': 'Other/Unknown'}})

    adult_data = adult_data.replace({'marital-status': {'Married-civ-spouse': 'Married',
                                                        'Married-AF-spouse': 'Married', 'Married-spouse-absent': 'Married', 'Never-married': 'Single'}})

    adult_data = adult_data.replace({'race': {'Black': 'Other', 'Asian-Pac-Islander': 'Other',
                                              'Amer-Indian-Eskimo': 'Other'}})

    adult_data = adult_data[['age', 'hours-per-week', 'workclass', 'education', 'marital-status',
                             'occupation', 'race', 'gender', 'income']]

    adult_data = adult_data.replace({'income': {'<=50K': 0, '>50K': 1}})

    adult_data = adult_data.replace({'education': {'Assoc-voc': 'Assoc', 'Assoc-acdm': 'Assoc',
                                                   '11th': 'School', '10th': 'School', '7th-8th': 'School', '9th': 'School',
                                                   '12th': 'School', '5th-6th': 'School', '1st-4th': 'School', 'Preschool': 'School'}})

    adult_data = adult_data.rename(
        columns={'marital-status': 'marital_status', 'hours-per-week': 'hours_per_week'})

    return adult_data

# Cell
def load_learning_analytic_data(path='../data/oulad'):
    def weighted_score(x):
        d = {}
        total_weight = sum(x['weight'])
        d['weight'] = total_weight
        if sum(x['weight']) == 0:
            d['weighted_score'] = sum(x['score']) / len(x['score'])
        else:
            d['weighted_score'] = sum(x['score'] * x['weight']) / sum(x['weight'])
        return pd.DataFrame(d, index=[0])

    def clicks(x):
        types = x['activity_type']
        sum_clicks = x['sum_click']
    #     for t, c in zip(types, sum_clicks):
    #         x[f"{t}_click"] = c
        return pd.DataFrame({f"{t}_click": c for t, c in zip(types, sum_clicks)}, index=[0])

    print('loading pandas dataframes...')

    assessment = pd.read_csv(f'{path}/assessments.csv')
    courses = pd.read_csv(f'{path}/courses.csv')
    student_assessment = pd.read_csv(f'{path}/studentAssessment.csv')
    student_info = pd.read_csv(f'{path}/studentInfo.csv')
    student_regist = pd.read_csv(f'{path}/studentRegistration.csv')
    student_vle = pd.read_csv(f'{path}/studentVle.csv')
    vle = pd.read_csv(f'{path}/vle.csv')

    print('preprocessing assessment...')

    # note: only count for submitted assessment, not weighted for unsubmitted ones
    assessment_merged = student_assessment.merge(assessment)
    assessment_grouped = assessment_merged.groupby(['code_module', 'code_presentation', 'id_student']).apply(weighted_score)
    assessment_df = assessment_grouped.reset_index(None).drop(['level_3'], axis=1)

    print('preprocessing vle...')

    # vle
    grouped_vle = student_vle.merge(vle).groupby(['activity_type', 'code_module', 'code_presentation', 'id_student'])
    sumed_vle = grouped_vle.sum().drop(['id_site', 'date', 'week_from', 'week_to'], axis=1).reset_index()
    grouped_vle = sumed_vle.groupby(['code_module', 'code_presentation', 'id_student']).apply(clicks)
    vle_df = grouped_vle.reset_index(None).drop(['level_3'], axis=1)

    student_df = student_info.merge(assessment_df, on=['code_module', 'code_presentation', 'id_student'], how='left')\
        .merge(vle_df, on=['code_module', 'code_presentation', 'id_student'], how='left')

    return student_df[['num_of_prev_attempts', 'weight', 'weighted_score',
                       'forumng_click', 'homepage_click', 'oucontent_click',
                       'resource_click', 'subpage_click', 'url_click', 'dataplus_click',
                       'glossary_click', 'oucollaborate_click', 'quiz_click',
                       'ouelluminate_click', 'sharedsubpage_click', 'questionnaire_click',
                       'page_click', 'externalquiz_click', 'ouwiki_click', 'dualpane_click',
                       'folder_click', 'repeatactivity_click', 'htmlactivity_click',
                                      'code_module', 'gender', 'region',
                       'highest_education', 'imd_band', 'age_band','studied_credits',
                       'disability', 'final_result']]

# Cell

class NumpyDataset(TensorDataset):
    def __init__(self, *arrs, ):
        super(NumpyDataset, self).__init__()
        # init tensors
        # small patch: skip continous or discrete array without content
        self.tensors = [torch.tensor(arr).float() for arr in arrs if arr.shape[-1] != 0]
        assert all(self.tensors[0].size(0) == tensor.size(0) for tensor in self.tensors)

    def data_loader(self, batch_size=128, shuffle=True, num_workers=4):
        return DataLoader(self, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)

    def features(self, test=False):
        return tuple(self.tensors[:-1] if not test else self.tensors)

    def target(self, test=False):
        return self.tensors[-1] if not test else None

class PandasDataset(NumpyDataset):
    def __init__(self, df: pd.DataFrame):
        cols = df.columns
        X = df[cols[:-1]].to_numpy()
        y = df[cols[-1]].to_numpy()
        super().__init__(X, y)

# Comes from 03b_counterfactual_net.ipynb, cell
def uniform(shape: tuple, r1: float, r2: float, device=None):
    assert r1 < r2
    return (r2 - r1) * torch.rand(*shape, device=device) + r1

# Comes from 03b_counterfactual_net.ipynb, cell
def hinge_loss(input, target):
    """ 
    reference:
    - https://github.com/interpretml/DiCE/blob/a772c8d4fcd88d1cab7f2e02b0bcc045dc0e2eab/dice_ml/explainer_interfaces/dice_pytorch.py#L196-L202
    - https://en.wikipedia.org/wiki/Hinge_loss
    """
    input = torch.log((abs(input - 1e-6) / (1 - abs(input - 1e-6))))
    all_ones = torch.ones_like(target)
    target = 2 * target - all_ones
    loss = all_ones - torch.mul(target, input)
    loss = F.relu(loss)
    return torch.norm(loss)

# Comes from 03b_counterfactual_net.ipynb, cell
def cat_normalize(c, cat_arrays, cat_idx,cont_shape,hard=False,used_carla=False):
    c_copy = c.clone()
    # categorical feature starting index
    for col in cat_arrays:
        
        cat_end_idx = cat_idx + len(col)
        if hard:
            if used_carla : 
                c_copy[:, cat_idx: cat_end_idx] = torch.round(F.sigmoid(c[:, cat_idx: cat_end_idx].clone())).long()
                
            else :
                c_copy[:, cat_idx: cat_end_idx] = F.gumbel_softmax(c[:, cat_idx: cat_end_idx].clone(), hard=hard)
        else:
            if used_carla : 
                c_copy[:, cat_idx: cat_end_idx] = F.sigmoid(c[:, cat_idx: cat_end_idx].clone())
            else : 
                # Softmax for categorical variables 
                c_copy[:, cat_idx: cat_end_idx] = F.softmax(c[:, cat_idx: cat_end_idx].clone(), dim=-1)
        cat_idx = cat_end_idx
    
        
    # Relu for all continious variables 
    c_copy[:,:cont_shape] = torch.relu(c[:,:cont_shape].clone())
    return c_copy

def l1_mean(x, c):
    return F.l1_loss(x, c, reduction='mean') / x.abs().mean() # MAD

_loss_functions = {
    'cross_entropy': F.binary_cross_entropy,
    'l1': F.l1_loss,
    'l1_mean': l1_mean,
    'mse': F.mse_loss
}

def get_loss_functions(f_name: str):
    assert f_name in _loss_functions.keys(), f'function name "{f_name}" is not in the loss function list {_loss_functions.keys()}'
    return _loss_functions[f_name]

_optimizers = {
    'adam': torch.optim.Adam
}

def get_optimizers(o_name: str):
    assert o_name in _optimizers.keys(), f'optimizer name "{o_name}" is not in the optimizer list {_optimizers.keys()}'
    return _optimizers[o_name]

def smooth_y(y, device=None):
    return torch.where(y == 1,
                       uniform(y.size(), 0.8, 0.95, device=y.device),
                       uniform(y.size(), 0.05, 0.2, device=y.device))





# Round columns in list_int 
def int_round_dataset(dataset,dico_round) : 
    dataset = dataset.copy()
    list_round = list(dico_round.keys())
    for column in list_round : 
        dataset[column] = dataset[column].apply(lambda x : round(x,dico_round[column]))
    return dataset


# Check if inverse min max scaler and rounding give the same results as before 
def check_min_max_scaler(dataset,original_examples,dico_round) : 
    # Round numerical values 
    original_examples_round = int_round_dataset(original_examples,dico_round) 
    # Round the original dataset 
    original_true_round = dataset.data[dataset.data.columns[:-1]]
    original_true_round = original_true_round[original_examples_round.columns]
    original_true_round = int_round_dataset(original_true_round,dico_round) 
    # Check if obtain the same values 
    index = len(original_true_round) - len(original_examples_round)
    original_true_round = original_true_round.loc[index:]
    same = np.array_equal(original_true_round.values,original_examples_round.values)
    return(same,original_examples_round)
    

# Back to the transform space 
def back_to_min_max(original_counterfactuals,dataset) :
    X_cont = dataset.normalizer.transform(original_counterfactuals[dataset.continous_cols]) if dataset.continous_cols else np.array([[] for _ in range(len(original_counterfactuals))])
    X_cat = dataset.encoder.transform(original_counterfactuals[dataset.discret_cols]) if dataset.discret_cols else np.array([[] for _ in range(len(original_counterfactuals))])
    X = np.concatenate((X_cont, X_cat), axis=1)
    return(torch.from_numpy(X).float())


from plot_distributions import numpy_to_dataframe
# Round counterfactuals numerical values for int 
def round_counterfactuals(X,results,dataset,training,dico_round) :
    # Examples and counterfactuals back to the original space 
    original_examples,original_counterfactuals = numpy_to_dataframe(X,results["cf"],dataset)
    orginal_examples_round = int_round_dataset(original_examples,dico_round) 
    #problem,orginal_examples_round = check_min_max_scaler(dataset,original_examples,dico_round)
    # Check if no problem with min max scaler of examples to explain 
    #print("Problem with rounding is",not problem)
    # Round counterfactuals columns as int 
    original_counterfactuals_round = int_round_dataset(original_counterfactuals,dico_round)
    # Counterfactuals in transform space with rounded values in original space 
    counterfactuals_min_max_round = back_to_min_max(original_counterfactuals_round,dataset)
    # Predicted proba for counterfactuals 
    proba_c = training.model.forward_pred(counterfactuals_min_max_round).squeeze(1)
    # percentage of counterfactuals that change predicted class when rounding 
    y_c = torch.round(proba_c).long()
    percentage = sum(y_c == results["y_c"])/results["y_c"].shape[0]
    # if not 100% validity
    if not bool(percentage==1.0) :
        print("Alert : Some class have changed after rounding")
        print("{:.2%} of counterfactuals are still valid".format(percentage))
        
    return {"X" : orginal_examples_round, # Examples
            "cf" : original_counterfactuals_round, # Counterfactuals
            "y_x" : results["y_x"], # Predicted examples classes
            "y_c" : y_c , #Predicted counterfactuals classes 
            "proba_x" : results["proba_x"], # Predicted probas for examples 
            "proba_c" : proba_c #Predicted probas for counterfactuals  
            }