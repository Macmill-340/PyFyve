def validate(result, rules, user_code):
    if "error" in result["status"]:
        print("❌ Task incomplete due to errors in your code.")
        return "Fail"

    if rules["type"] == "variable_check":
        user_variables = result["variables"]
        target_variables = rules["var_info"]
        if target_variables.keys() <= user_variables.keys(): #check if all keys in target variables is in user variables
            extra_variables = user_variables.keys() - target_variables.keys() #check if user variable has extra keys
            if extra_variables:
                print(f"Note: You created extra variables: {extra_variables}")
            shared_keys = user_variables.keys() & target_variables.keys()
            mismatch = {k for k in shared_keys if target_variables[k] != user_variables[k]} #check if any shared keys has mismatched values
            if not mismatch:
                return "Pass"
            else:
                # Check if any mismatch is a type issue
                # e.g. stamina = "90" (str) instead of stamina = 90 (int)
                type_mismatches = {k for k in mismatch if type(user_variables[k]) != type(target_variables[k])}
                if type_mismatches:
                    for k in type_mismatches:
                        expected_type = type(target_variables[k]).__name__
                        got_type = type(user_variables[k]).__name__
                        print(f"❌ Variable '{k}' has the wrong type: expected {expected_type}, got {got_type}.")
                        return "Fail"
                print("❌ Task incomplete, please check values assigned to the variables.")
                return "Fail"
        else:
            print("❌ Task incomplete, all required variables not found.")
            return "Fail"

    if rules["type"] == "output_check":
        user_output = result["output"].strip()
        target_output = rules["expected_output"].strip()
        if target_output == user_output:
            return "Pass"
        else:
            print("❌ Task incomplete, please check task for required output and try again")
            return "Fail"

    if rules["type"] == "type_check":
        type_map = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
        }
        user_variables = result["variables"]
        target_variables = rules["var_info"]
        if target_variables.keys() <= user_variables.keys():  # check if all keys in target variables is in user variables
            extra_variables = user_variables.keys() - target_variables.keys()  # check if user variable has extra keys
            if extra_variables:
                print(f"Note: You created extra variables: {extra_variables}")
            shared_keys = user_variables.keys() & target_variables.keys()
            for key in shared_keys:
                target_type = type_map.get(target_variables[key])
                if not isinstance(user_variables[key], target_type):
                    print("❌ Task incomplete, please check that the value assigned is of correct type.")
                    return "Fail"
            else:
                return "Pass"
        else:
            print("❌ Task incomplete, required variable not found.")
            return "Fail"

    if rules["type"] == "source_check":
        if rules["required_syntax"].lower() in user_code.lower():
            return "Pass"
        else:
            print("❌ Task incomplete.\nIt is suspected that you are not using the methods referenced in the lesson.\nAvoid printing only the output if any particular method is asked to achieve the output.\nIf you are already using correct method, avoid naming variables the same as python functions such as 'while' or 'for'.")
            return "Fail"

    if rules["type"] == "collection_check":
        user_variables = result["variables"]
        target_variables = rules["var_info"]
        if target_variables.keys() <= user_variables.keys():  # check if all keys in target variables is in user variables
            extra_variables = user_variables.keys() - target_variables.keys()  # check if user variable has extra keys
            if extra_variables:
                print(f"Note: You created extra variables: {extra_variables}")
            # shared_keys = user_variables.keys() & target_variables.keys()
            for var in target_variables:
                if target_variables[var]["type"] == "list":
                    if not isinstance(user_variables[var], list):
                        print(f"❌ Task incomplete. '{user_variables[var]}' should be a list.")
                        return "Fail"
                    if"size" in target_variables[var] and len(user_variables[var]) != target_variables[var]["size"]:
                        print("❌ Task incomplete. Variable data structure is not of the required size.")
                        return "Fail"
                    if "contains" in target_variables[var]:
                        for items in target_variables[var]["contains"]:
                            if not items in user_variables[var]:
                                print(f"❌ Task incomplete. Required key or value not found in the variable {var}")
                                return "Fail"
                elif target_variables[var]["type"] == "dict":
                    if not isinstance(user_variables[var], dict):
                        print(f"❌ Task incomplete. '{user_variables[var]}' should be a dictionary.")
                        return "Fail"
                    if"size" in target_variables[var] and len(user_variables[var]) != target_variables[var]["size"]:
                        print("❌ Task incomplete. Variable data structure is not of the required size.")
                        return "Fail"
                    if "contains" in target_variables[var]:
                        if not target_variables[var]["contains"].items() <= user_variables[var].items():
                            print("❌ Task incomplete. The dictionary key-value pair you created does not match the requirements of the lesson")
                            return "Fail"
            else:
                return "Pass"
        else:
            print("❌ Task incomplete, all required variables not found.")
            return "Fail"






    # if rules["type"] == "function_check":

    else:
        return "Pass"