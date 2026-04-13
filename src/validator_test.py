from console import console


def validate(result, rules, user_code):
    if "error" in result["status"]:
        console.print("❌ Task incomplete due to errors in your code.", style="error")
        return "Fail"

    if rules["type"] == "variable_check":
        user_variables = result["variables"]
        target_variables = rules["var_info"]
        if target_variables.keys() <= user_variables.keys():
            extra_variables = user_variables.keys() - target_variables.keys()
            if extra_variables:
                console.print(f"Note: You created extra variables: {extra_variables}", style="info")
            shared_keys = user_variables.keys() & target_variables.keys()
            mismatch = {k for k in shared_keys if target_variables[k] != user_variables[k]}
            if not mismatch:
                return "Pass"
            else:
                type_mismatches = {k for k in mismatch if type(user_variables[k]) != type(target_variables[k])}
                if type_mismatches:
                    console.print("❌ Task incomplete — one or more variables has the wrong type. Check what kind of value you assigned.", style="error")
                    return "Fail"
                console.print("❌ Task incomplete — check the values assigned to your variables.", style="error")
                return "Fail"
        else:
            console.print("❌ Task incomplete — not all required variables were found.", style="error")
            return "Fail"

    if rules["type"] == "output_check":
        user_output = result["output"].strip()
        target_output = rules["expected_output"].strip()
        if target_output == user_output:
            return "Pass"
        else:
            console.print("❌ Task incomplete — check the task for the required output and try again.", style="error")
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
        if target_variables.keys() <= user_variables.keys():
            extra_variables = user_variables.keys() - target_variables.keys()
            if extra_variables:
                console.print(f"Note: You created extra variables: {extra_variables}", style="info")
            shared_keys = user_variables.keys() & target_variables.keys()
            for key in shared_keys:
                target_type = type_map.get(target_variables[key])
                if not isinstance(user_variables[key], target_type):
                    console.print("❌ Task incomplete — check that the value assigned is of the correct type.", style="error")
                    return "Fail"
            else:
                return "Pass"
        else:
            console.print("❌ Task incomplete — required variable not found.", style="error")
            return "Fail"

    if rules["type"] == "source_check":
        if rules["required_syntax"].lower() in user_code.lower():
            return "Pass"
        else:
            console.print("❌ Task incomplete.", style="error")
            console.print("It is suspected that you are not using the methods referenced in the lesson.", style="error")
            console.print("Avoid printing only the output if any particular method is asked to achieve the output.", style="info")
            console.print("If you are already using the correct method, avoid naming variables the same as Python keywords such as 'while' or 'for'.", style="info")
            return "Fail"

    if rules["type"] == "collection_check":
        user_variables = result["variables"]
        target_variables = rules["var_info"]
        if target_variables.keys() <= user_variables.keys():
            extra_variables = user_variables.keys() - target_variables.keys()
            if extra_variables:
                console.print(f"Note: You created extra variables: {extra_variables}", style="info")
            for var in target_variables:
                if target_variables[var]["type"] == "list":
                    if not isinstance(user_variables[var], list):
                        console.print("❌ Task incomplete — check the type of your collection.", style="error")
                        return "Fail"
                    if "size" in target_variables[var] and len(user_variables[var]) != target_variables[var]["size"]:
                        console.print("❌ Task incomplete — your collection is not the required size.", style="error")
                        return "Fail"
                    if "contains" in target_variables[var]:
                        for items in target_variables[var]["contains"]:
                            if not items in user_variables[var]:
                                console.print("❌ Task incomplete — check the contents of your collection.", style="error")
                                return "Fail"
                elif target_variables[var]["type"] == "dict":
                    if not isinstance(user_variables[var], dict):
                        console.print("❌ Task incomplete — check the type of your collection.", style="error")
                        return "Fail"
                    if "size" in target_variables[var] and len(user_variables[var]) != target_variables[var]["size"]:
                        console.print("❌ Task incomplete — your collection is not the required size.", style="error")
                        return "Fail"
                    if "contains" in target_variables[var]:
                        if not target_variables[var]["contains"].items() <= user_variables[var].items():
                            console.print("❌ Task incomplete — check the key-value pairs in your dictionary.", style="error")
                            return "Fail"
            else:
                return "Pass"
        else:
            console.print("❌ Task incomplete — not all required variables were found.", style="error")
            return "Fail"

    # Unknown validation type — fail loudly so lesson authors catch mistakes in their JSON
    console.print(f"❌ Unknown validation type: '{rules['type']}'. Check your lesson JSON.", style="error")
    return "Fail"
