#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Huawei Device Co., Ltd.
#
# HDF is dual licensed: you can use it either under the terms of
# the GPL, or the BSD license, at your option.
# See the LICENSE file in the root of this repository for complete details.


from string import Template

import hdf_utils

from .gn_file_add_config import judge_driver_config_exists


def find_makefile_file_end_index(date_lines, model_name):
    file_end_flag = "include $(HDF_DRIVER)"
    end_index = 0
    model_dir_name = ("%s_ROOT_DIR" % model_name.upper())
    model_dir_value = ""

    for index, line in enumerate(date_lines):
        if line.startswith("#"):
            continue
        elif line.strip().startswith(file_end_flag):
            end_index = index
        elif line.strip().startswith(model_dir_name):
            model_dir_value = line.split("=")[-1].strip()
        else:
            continue
    result_tuple = (end_index, model_dir_name, model_dir_value)
    return result_tuple


def makefile_file_operation(path, driver_file_path, module, driver):
    makefile_gn_path = path
    date_lines = hdf_utils.read_file_lines(makefile_gn_path)
    judge_result = judge_driver_config_exists(date_lines, driver_name=driver)
    if judge_result:
        return
    source_file_path = driver_file_path.replace('\\', '/')
    result_tuple = find_makefile_file_end_index(date_lines, model_name=module)
    end_index, model_dir_name, model_dir_value = result_tuple
    
    first_line = "\nifeq ($(LOSCFG_DRIVERS_HDF_${model_name_upper}_${driver_name_upper}), y)\n"
    second_line = "LOCAL_SRCS += $(${model_name_upper}_ROOT_DIR)/${source_file_path}\n"
    third_line = "endif\n"
    makefile_add_template = first_line + second_line + third_line
    include_model_info = model_dir_value.split("model")[-1].strip('"')+"/"
    makefile_path_config = source_file_path.split(include_model_info)
    temp_handle = Template(makefile_add_template.replace("$(", "temp_flag"))
    d = {
        'model_name_upper': module.upper(),
        'driver_name_upper': driver.upper(),
        'source_file_path': makefile_path_config[-1]
    }
    new_line = temp_handle.substitute(d).replace("temp_flag", "$(")

    date_lines = date_lines[:end_index-1] + [new_line] + date_lines[end_index-1:]
    hdf_utils.write_file_lines(makefile_gn_path, date_lines)
