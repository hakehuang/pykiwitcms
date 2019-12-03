from tcms_api import TCMS
import ssl

#need config ~/.tcms.conf as below
'''
[tcms]
url=https://92.120.145.188/xml-rpc/
username=hake.huang@nxp.com
password=Happy123
verify=False
'''

#remove the SSL authoriztion error 
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context



def connect():
    rpc_client = TCMS().exec
    return rpc_client


def get_function_by_type(rpc_client, type, func_type="query"):
    TYPE_LIST = { 
        "query" : {
            "TestCase" : rpc_client.TestCase.filter,
            "Product" : rpc_client.Product.filter, 
            "Category" : rpc_client.Category.filter,
            "Priority" : rpc_client.Priority.filter,
            "Component": rpc_client.Component.filter,
            "Build" : rpc_client.Build.filter,
            "TestCaseRun" : rpc_client.TestCaseRun.filter,
            "TestCaseStatus" : rpc_client.TestCaseStatus.filter,
            "TestPlan" : rpc_client.TestPlan.filter,
            "TestRun" : rpc_client.TestRun.filter,
            "User" : rpc_client.User.filter,
            "Version" : rpc_client.Version.filter,
            "Plantype": rpc_client.PlanType.filter,
            "EnvGroup": rpc_client.Env.Group.filter,
            "EnvValue": rpc_client.Env.Value.filter,
            },
        "create" : {
            "TestCase" : rpc_client.TestCase.create,
            "Product" : rpc_client.Product.create, 
            "Component": rpc_client.Component.create,
            "Build" : rpc_client.Build.create,
            "TestCaseRun" : rpc_client.TestCaseRun.create,
            "TestCaseStatus" : rpc_client.TestCaseStatus.create,
            "TestPlan" : rpc_client.TestPlan.create,
            "TestRun" : rpc_client.TestRun.create,
            "User" : rpc_client.User.create,
            "Version" : rpc_client.Version.create,
            "Plantype": rpc_client.PlanType.create,
            },
        }

    if type not in TYPE_LIST[func_type].keys():
        print("shall be one of %s"% TYPE_LIST[func_type].keys())
        return None
    return TYPE_LIST[func_type][type]

def get_all_items(rpc_client, type):
    fn = get_function_by_type(rpc_client, type)
    if fn == None:
        return None
    print("all %s are:"% type)
    for item in fn({}):
        print("-\t" + str(item))
    return fn({})

def query_item(rpc_client, type, hash):
    fn = get_function_by_type(rpc_client, type)
    if fn == None:
        print("not found")
        return None
    #for item in fn(hash):
    #    print("-\t" + str(item))
    return fn(hash)

def creat_case(rpc_client ,hash):
    '''
    values = {
    'category': 135,
    'product': 61,
    'summary': 'Testing XML-RPC',
    'priority': 1,
    }
    '''
    mdict = {}
    for item in hash:
        if hash[item].__class__.__name__ == "dict":
            key = list(hash[item].keys())[0]
            content = get_all_items(rpc_client, item.capitalize())
            for cn in content:
                if key in cn and cn[key] == hash[item][key]:
                    mdict[item] = cn['id']
        else:
            mdict[item] = hash[item]
    #print("create case with")
    #print(mdict)
    result = rpc_client.TestCase.create(mdict)
    return result

def update_case(rpc_client, case_id, hash):
    '''
    case_id (int - PK of TestCase to be modified
    values (dict - Field values for tcms.testcases.models.TestCase 
                    The special keys setup, breakdown, action and effect are recognized 
                    and will cause update of the underlying tcms.testcases.models.TestCaseText object!
    hash = {
        'setup' : 'do setup',
        'breakdown' : 'do break down',
        'action' : 'do action',
        'effect' : 'effect'
    }
    '''
    print(hash)
    res = rpc_client.TestCase.update(case_id, hash)
    return res

def case_add_component(rpc_client, case_id, component):
    '''
    in case_id: case id in kiwi
    in component: component name
    '''
    cp = query_item(rpc_client, "Component", {'name' : component})
    if len(cp):
        rpc_client.TestCase.add_component(case_id, cp[0]['id'])

def case_get_components(rpc_client, case_id):
    return rpc_client.TestCase.get_components(case_id)


def case_remove_component(rpc_client, case_id, component):
    '''
    in case_id: case id in kiwi
    in component: component name
    '''
    cp = query_item(rpc_client, "Component", {'name' : component})
    if len(cp):
        rpc_client.TestCase.remove_component(case_id, cp[0]['id'])


def create_component(rpc_client, hash):
    '''
    in hash = {
        'description' : "",
        'name'        : "FRDMK64F"
    }
    '''
    values = {}
    #values['description'] = hash['description']
    values['name'] = hash['name']
    pn = query_item(rpc_client, "Product", {'name': hash['product']})
    if len(pn) == 0:
        print("not product find %s",hash['product'])
        return None
    values['product'] = pn[0]['id']
    cm = query_item(rpc_client, "Component", values)
    if len(cm) == 0:
        fn = get_function_by_type(rpc_client, "Component",  "create")
        if fn == None:
            print("no create fuction")
        else:
            return fn(hash)
    else:
        print("comonent %s already has id is %s", values,cm[0]['id'])


def create_case_with_componet(rpc_client, case_hash, component):
    cs = creat_case(rpc_client, case_hash)
    case_add_component(rpc_client, cs['case_id'], component)
    return cs


def creat_plan(rpc_client ,values):
    '''
    in values = {
    'product': 'MCU_SDK',
    'name': 'Testplan foobar',
    'type': 1,
    'default_product_version': 1,
    'text':'Testing TCMS',
    }
    '''
    p = {}
    pn = query_item(rpc_client, "Product", {'name': values['product']})
    #print(pn)
    p['product'] = pn[0]['id']
    t = query_item(rpc_client, "Plantype", {'name': values['type']})
    p['type'] = t[0]['id']
    pv = query_item(rpc_client, "Version", {'value': values['default_product_version']})
    #print(pv)
    p['default_product_version'] = pv[0]['id']
    p['name'] = values['name']
    p['text'] = values['text']
    result = rpc_client.TestPlan.create(p)
    return result

def add_case_to_plan(rpc_client , plan_id, case_id):
    rpc_client.TestPlan.add_case(plan_id, case_id)

def confirm_plan(rpc_client , plan_id):
    rpc_client.TestPlan.update(plan_id, {'is_active': True})


def test_add_case_to_plan():
    '''
{'id': 5, 'name': 'Acceptance', 'description': ''}
{'id': 3, 'name': 'Function', 'description': ''}
{'id': 6, 'name': 'Installation', 'description': ''}
{'id': 2, 'name': 'Integration', 'description': ''}
{'id': 9, 'name': 'Interoperability', 'description': ''}
{'id': 7, 'name': 'Performance', 'description': ''}
{'id': 8, 'name': 'Product', 'description': ''}
{'id': 11, 'name': 'Regression', 'description': ''}
{'id': 10, 'name': 'Smoke', 'description': ''}
{'id': 4, 'name': 'System', 'description': ''}
{'id': 1, 'name': 'Unit', 'description': ''}
    '''
    rpc_client = connect()
    values = {
    'product': 'MCU_SDK',
    'name': 'Testplan foobar',
    'type': 'Function',
    'default_product_version': 'TEST_EAR',
    'text':'Testing TCMS', 
    }
    p = creat_plan(rpc_client,values)
    print(p)
    add_case_to_plan(rpc_client, str(p['plan_id']), '1')
    confirm_plan(rpc_client, str(p['plan_id']))

def test_get_all_items():
    rpc_client = connect()
    get_all_items(rpc_client, "TestCase")
    get_all_items(rpc_client, "Product")
    get_all_items(rpc_client, "Category")
    get_all_items(rpc_client, "Priority")
    get_all_items(rpc_client, "Component")
    get_all_items(rpc_client, "Build")
    get_all_items(rpc_client, "TestCaseRun")
    get_all_items(rpc_client, "TestCaseStatus")
    get_all_items(rpc_client, "TestPlan")
    get_all_items(rpc_client, "TestRun")
    get_all_items(rpc_client, "User")
    get_all_items(rpc_client, "Version")
    get_all_items(rpc_client, "Plantype")
    get_all_items(rpc_client, "EnvGroup")
    get_all_items(rpc_client, "EnvValue")

def test_query_item():
    rpc_client = connect()
    query_item(rpc_client, "TestCase", {'case_id': 1})
    query_item(rpc_client, "TestCase", {'summary': 'hello world'})
    query_item(rpc_client, "Product", {'id': 1})
    query_item(rpc_client, "Product", {'name': 'MCU_SDK'})
    query_item(rpc_client, "Category", {'id': 2})
    query_item(rpc_client, "Category", {'name': 'Demo'})
    query_item(rpc_client, "Priority", {'id': 1})
    query_item(rpc_client, "Priority", {'value': 'P1'})
    query_item(rpc_client, "Component", {'id': 1})
    query_item(rpc_client, "Component", {'name': 'FRDMK64F'})
    query_item(rpc_client, "Build", {'build_id': 1})
    query_item(rpc_client, "Build", {'name': 'unspecified'})
    query_item(rpc_client, "TestCaseRun", {'case_run_id': 1, 'run_id': 1})
    query_item(rpc_client, "TestCaseRun", {'case_run_id': 1, 'run_id': 1})
    query_item(rpc_client, "TestCaseStatus", {'name': 'PROPOSED'})
    query_item(rpc_client, "TestCaseStatus", {'id': 1})
    query_item(rpc_client, "TestPlan", {'name': 'test plan trial'})
    query_item(rpc_client, "TestPlan", {'plan_id': 3})
    query_item(rpc_client, "TestRun", {'run_id': 1})
    query_item(rpc_client, "User", {'username': 'hake.huang@nxp.com'})
    query_item(rpc_client, "Version", {'value': 'TEST_EAR'})
    query_item(rpc_client, "Plantype", {'id': '1'})
    query_item(rpc_client, "EnvGroup", {'id': '1'})


def test_create_case():
    values = {
    'category': {'name': 'Demo'},
    'product': {'name': 'MCU_SDK'},
    'summary': 'Testing XML-RPC',
    'priority': 1,
    'estimated_time' : "00:00:05",
    }
    rpc_client = connect()
    res = creat_case(rpc_client, values)
    print(res)

def test_update_case():
    hash = {
        'setup' : 'do setup2',
        'breakdown' : 'do break down',
        'action' : 'do action',
        'effect' : 'effect'
    }
    rpc_client = connect()
    res = update_case(rpc_client, '3', hash)
    print(res)

def test_case_component():
    rpc_client = connect()
    cs = query_item(rpc_client, "TestCase", {'summary': 'Testing XML-RPC'})
    print(cs)
    cc = case_get_components(rpc_client, cs[0]['case_id'])
    print(cc)
    if len(cc) == 0:
        cm_name = "FRDMK64F"
        case_remove_component(rpc_client, cs[0]['case_id'], cm_name)
        cc = case_get_components(rpc_client, cs[0]['case_id'])
        print(cc)
    else:
        cm_name = cc[0]['name']

    case_add_component(rpc_client, cs[0]['case_id'], cm_name)
    cc = case_get_components(rpc_client, cs[0]['case_id'])
    print(cc)

def test_add_component():
    hash = {
        'product': 'MCU_SDK',
        'description' : "SDK",
        'name'        : "FRDMKW41Z"
    }
    rpc_client = connect()
    cm = create_component(rpc_client ,hash)
    print(cm)

def test_create_case_with_componet():
    rpc_client = connect()
    values = {
    'category': {'name': 'Demo'},
    'product': {'name': 'MCU_SDK'},
    'summary': 'Testing create case with component',
    'priority': 1,
    'estimated_time' : "00:00:05",
    }
    create_case_with_componet(rpc_client, values, "FRDMK64F")

if __name__ == "__main__":
    test_get_all_items()
    #test_query_item()
    #test_create_case()
    #test_update_case()
    #test_add_case_to_plan()
    #test_case_component()
    #test_add_component()
    #test_create_case_with_componet()
