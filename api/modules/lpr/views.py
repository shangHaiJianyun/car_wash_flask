# -*- coding: utf-8 -*-
# @Time    : 19-1-4 下午1:19
from flask import request, jsonify
# from werkzeug.utils import secure_filename
#
# from api.modules.lpr import lpr_blu
# from hyperlpr import *
# # 导入OpenCV库
# import cv2
#
#
# @lpr_blu.route('/lpr', methods=['POST'])
# def lprM():
#     # 读入图片
#     f = request.files['file']
#     basepath = sys.path[0]  # 当前文件所在路径
#
#     upload_path = os.path.join(basepath + '/api/static/images', secure_filename(f.filename))  # 先将传递的图片存入本地
#     f.save(upload_path)
#
#     # 使用Opencv转换一下图片格式和名称
#     img = cv2.imread(upload_path)
#     # 识别结果
#     data = HyperLPR_PlateRecogntion(img)
#
#     if data:
#         for i in data:
#             if i[1] > 0.8:
#                 os.remove(upload_path)
#                 return jsonify({'lp': i[0]})
#     else:
#         return jsonify('error happens')
