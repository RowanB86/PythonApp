import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np
import random
from scipy import stats
from scipy.stats import poisson
import time
import copy
import json


st.set_page_config(layout="wide") 

class KDEDist(stats.rv_continuous):
    
    def __init__(self, kde, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._kde = kde
    
    def _pdf(self, x):
        return self._kde.pdf(x)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def update_session_state():

    new_state = copy.deepcopy([
        json.loads(json.dumps(st.session_state.edges)),  
        json.loads(json.dumps(st.session_state.nodes)),
        json.loads(json.dumps(st.session_state.clicked_nodes)),
        st.session_state.selected_node,
        st.session_state.canvas_clicked,
        json.loads(json.dumps(st.session_state.bboxes)),
        json.loads(json.dumps(st.session_state.bboxes_dict)),
        json.loads(json.dumps(st.session_state.bbox_details)),
        st.session_state.drawing_mode,
        st.session_state.node_selected,
        st.session_state.rerun,
        st.session_state.selected_edge,
        st.session_state.previous_selected_edge,
        st.session_state.click_behaviour,
        st.session_state.delete_confirmation,
        st.session_state.selection_bbox if 'selection_bbox' in st.session_state else None,
        st.session_state.speed_mean_factor if 'speed_mean_factor' in st.session_state else None,
        st.session_state.speed_var_factor if 'speed_var_factor' in st.session_state else None
    ])              
    


    if (len(st.session_state.state_history) - 1) > st.session_state.state_num:

        st.session_state.state_history = copy.deepcopy(st.session_state.state_history[:st.session_state.state_num + 1])


    st.session_state.state_history.append(new_state)


    st.session_state.state_num = len(st.session_state.state_history) - 1

def resize_image(img_path, target_height):
    img = Image.open(img_path).convert("RGBA")  
    original_width, original_height = img.size
    img.thumbnail((target_height, target_height), Image.LANCZOS)  
    new_width, new_height = img.size
    return img, original_width, original_height, new_width, new_height

def point_on_line(x1,y1,line):
    
    line_x1 = line[0]
    line_y1 = line[1]
    line_x2 = line[2]
    line_y2 = line[3]
    
    gradient = (line_y2 - line_y1) / (line_x2 - line_x1)
    
    c = line_y1 - (line_x1*gradient)
    
    point_c = y1 - (x1*gradient)
    
    upper_c = c + 10
    lower_c = c - 10
    
    lower_line = (line_x1,line_x1*gradient + lower_c, line_x2, line_x2*gradient + lower_c)
    upper_line = (line_x1,line_x1*gradient + upper_c, line_x2, line_x2*gradient + upper_c)
    
    on_line =  True

    if not line_x1 < x < line_x2:#
        on_line = False
        
        
    if not lower_c <= point_c <= upper_c:
        on_line = False
    

    return on_line, lower_line, upper_line

def getBoundingBox(img_path,target_height,x,y):

    img, original_w, original_h, new_w, new_h = resize_image(img_path, target_height)
    bbox = img.getbbox()

    #x = x - new_w // 2
    #y = y - new_h // 2

    bounding_box = (x + bbox[0]-2, y + bbox[1]-2, x + bbox[2], y + bbox[3])               

    
    return bounding_box

def empirical_cdf(data):
    data_sorted = np.sort(data)
    cdf_vals = np.arange(1, len(data_sorted)+1) / len(data_sorted)
    return data_sorted, cdf_vals

def Fire_ROP_MSH_Calc(Avg_Usage,Avg_LT,StDev_LT,Re_Order_Freq,combat_hours,ProbStockout=0.005):
    
    Avg_Usage = float(Avg_Usage)
    Avg_LT = float(Avg_LT)
    StDev_LT = float(StDev_LT)
    Re_Order_Freq = int(Re_Order_Freq)
    ProbStockout = float(ProbStockout)
    combat_hours = float(combat_hours)
    
    st.write('Avg_usage' + str(Avg_Usage))
    st.write('Avg_LT' + str(Avg_LT))
    st.write('StDev_LT' + str(StDev_LT))
    st.write('Re_Order_Freq' + str(Re_Order_Freq))
    st.write('Prob stockout' + str(ProbStockout))
    st.write('combat hours' + str(combat_hours))
    
    LT_sample = np.random.normal(Avg_LT, StDev_LT, 1000)
    usage_sample = np.random.poisson(Avg_Usage, 1000)
    
    data = [None] * 1000

    for i in range(0,1000):
        LT = random.sample(list(LT_sample),1)
        LT_int = max(int(LT[0]),1)                  
        data[i] = np.sum(random.sample(list(usage_sample),LT_int))   
    
    kde = stats.gaussian_kde(data, bw_method=0.5)    
    X = KDEDist(kde)
    x = np.linspace(0, max(data) + 3 * np.std(data), 100)
    cdfVals = np.array([kde.integrate_box_1d(0, xi) for xi in x])

    Quantile = 1 - ProbStockout
    try:
        min_val = min(i for i in cdfVals if i > (1-ProbStockout))   
    except:
        min_val = min(i for i in cdfVals if i > (1-max(cdfVals-0.01)))
    min_val_ind = cdfVals.tolist().index(min_val)    
    
    UB1 = x[min_val_ind]
    LB1 = x[min_val_ind-1]
    
    Rng1 = UB1 - LB1
    
    UB2 = cdfVals[min_val_ind]
    LB2 = cdfVals[min_val_ind-1]

    Rng2 = UB2 - LB2
    Factor = (Quantile-LB2) / Rng2
    ROP = round(LB1 + (Factor*Rng1),0)
    
    try:
        median_val = min(i for i in cdfVals if i > 0.5)   
    except:
        median_val = min(i for i in cdfVals if i > (1-max(cdfVals-0.01)))
        
    median_val_ind = cdfVals.tolist().index(median_val)

    UB1 = x[median_val_ind]
    LB1 = x[median_val_ind-1]
    
    Rng1 = UB1 - LB1
    
    UB2 = cdfVals[median_val_ind]
    LB2 = cdfVals[median_val_ind-1]

    Rng2 = UB2 - LB2
    Factor = (0.5-LB2) / Rng2
    AvgLTD = LB1 + (Factor*Rng1)
    
    SS = ROP - AvgLTD
    
    ROQ = round(((60*combat_hours) / Re_Order_Freq) * Avg_Usage,0)
    MSH = round(SS + ROQ,0)
    ROP = round(ROP,0)
    SS = round(SS,0)
    
    return ROP, ROQ, MSH,SS

def ROP_MSH_Calc(ROF_ROQ_List, Avg_LT, StDev_LT, Re_Order_Freq,  combat_hours,ProbStockout=0.005):
    Avg_LT = float(Avg_LT)
    StDev_LT = float(StDev_LT)
    Re_Order_Freq = int(Re_Order_Freq)
    ProbStockout = float(ProbStockout)
    combat_hours = float(combat_hours)

    data = [None] * 1000
    LT_sample = np.random.normal(Avg_LT, StDev_LT, 1000)

    for i in range(1000):
        LT_int = max(int(LT_sample[i]), 1)
        total_usage = 0
        for j in range(len(ROF_ROQ_List)):
            ROF = ROF_ROQ_List[j][0]
            ROQ = float(ROF_ROQ_List[j][1])
            total_usage += np.sum(np.random.poisson((ROF/(combat_hours*60))*ROQ, LT_int)) 
        data[i] = total_usage
        


    sorted_data, cdfVals = empirical_cdf(data)

    Quantile = 1 - ProbStockout
    above_threshold_vals = sorted_data[cdfVals >= Quantile]

    if len(above_threshold_vals) == 0:
        ROP = sorted_data[-1]  # max value
    else:
        ROP = above_threshold_vals[0]

    Quantile = 0.5
    above_threshold_vals = sorted_data[cdfVals >= Quantile]

    if len(above_threshold_vals) == 0:
        AvgLTD = sorted_data[-1]  # max value
    else:
        AvgLTD = above_threshold_vals[0]
    
    SS = ROP - AvgLTD
    Avg_Usage = 0
    
    for j in range(len(ROF_ROQ_List)):
        Avg_Usage += (ROF_ROQ_List[j][0] / (60 * combat_hours))*ROF_ROQ_List[j][1]

    ROQ = round(((60 * combat_hours) / Re_Order_Freq) * Avg_Usage,0)
    MSH = round(SS + ROQ,0)
    ROP = round(ROP,0)
    SS = round(SS,0)

    return ROP, ROQ, MSH, SS

def draw_edge(selected_bbox,bbox,draw):
    

    if bbox[2] < selected_bbox[0]:
        right_bbox = selected_bbox
        
        x1 = bbox[2]
        y1 = bbox[1] + ((bbox[3] - bbox[1])/2)
        
        x2 = selected_bbox[0]
        y2 = right_bbox[1] + ((right_bbox[3] - right_bbox[1])/2)
        
        bbox_key = f"{round(bbox[0])}_{round(bbox[1])}_{round(bbox[2])}_{round(bbox[3])}"
        right_bbox_key = f"{round(right_bbox[0])}_{round(right_bbox[1])}_{round(right_bbox[2])}_{round(right_bbox[3])}"
        
        bbox_ID = st.session_state.bbox_details[bbox_key]["ID"]
        right_bbox_ID = st.session_state.bbox_details[right_bbox_key]["ID"]
        
        left_bbox_type = st.session_state.bbox_details[bbox_key]["type"]
        right_bbox_type = st.session_state.bbox_details[right_bbox_key]["type"] 
        
        if draw:
        
            st.session_state.edges.append({"left_bbox_ID": bbox_ID,"right_bbox_ID": right_bbox_ID, \
                                           "left_bbox_type": left_bbox_type,"right_bbox_type": right_bbox_type ,"line": (x1,y1,x2,y2),"length": 0}) 
                
        else:
            return (x1,y1,x2,y2)
            
    
    elif selected_bbox[2] <= bbox[0]:
        
        left_bbox = selected_bbox
    
        x1 = left_bbox[2]
        y1 = left_bbox[1] + ((left_bbox[3] - left_bbox[1])/2)
        
        x2 = bbox[0]
        y2 = bbox[1] + ((bbox[3] - bbox[1])/2)
        
        if draw:
        
            bbox_key = f"{round(left_bbox[0])}_{round(left_bbox[1])}_{round(left_bbox[2])}_{round(left_bbox[3])}"
            right_bbox_key = f"{round(bbox[0])}_{round(bbox[1])}_{round(bbox[2])}_{round(bbox[3])}"
            
            bbox_ID = st.session_state.bbox_details[bbox_key]["ID"]
            right_bbox_ID = st.session_state.bbox_details[right_bbox_key]["ID"]
            
            left_bbox_type = st.session_state.bbox_details[bbox_key]["type"]
            right_bbox_type = st.session_state.bbox_details[right_bbox_key]["type"]
        
            
            st.session_state.edges.append({"left_bbox_ID": bbox_ID,"right_bbox_ID": right_bbox_ID, \
                                           "left_bbox_type": left_bbox_type,"right_bbox_type": right_bbox_type ,"line": (x1,y1,x2,y2),"length": 0}) 
                
        else:
            
            return (x1,y1,x2,y2)
            
    elif selected_bbox[1] <= bbox[3]:
        
        upper_bbox= selected_bbox
        
        x1 = upper_bbox[0] + (upper_bbox[2] - upper_bbox[0]) / 2
        y1 = upper_bbox[3]
        
        x2 = bbox[0] + (bbox[2] - bbox[0]) / 2
        y2 = bbox[1]
        
        left_bbox_key = f"{round(upper_bbox[0])}_{round(upper_bbox[1])}_{round(upper_bbox[2])}_{round(upper_bbox[3])}"
        right_bbox_key = f"{round(bbox[0])}_{round(bbox[1])}_{round(bbox[2])}_{round(bbox[3])}"
    
        left_bbox_ID = st.session_state.bbox_details[left_bbox_key]["ID"]
        right_bbox_ID = st.session_state.bbox_details[right_bbox_key]["ID"]
        
        left_bbox_type = st.session_state.bbox_details[left_bbox_key]["type"]
        right_bbox_type = st.session_state.bbox_details[right_bbox_key]["type"]
        
        if draw:
        
            st.session_state.edges.append({"left_bbox_ID": left_bbox_ID,"right_bbox_ID": right_bbox_ID, \
                                           "left_bbox_type": left_bbox_type,"right_bbox_type": right_bbox_type ,"line": (x1,y1,x2,y2),"length": 0})
        else:
            
            return (x1,y1,x2,y2)
            
    else:
        
        lower_bbox= selected_bbox
        
        x1 = lower_bbox[0] + (lower_bbox[2] - lower_bbox[0]) / 2
        y1 = lower_bbox[1]
        
        x2 = bbox[0] + (bbox[2] - bbox[0]) / 2
        y2 = bbox[3]
        
        left_bbox_key = f"{round(lower_bbox[0])}_{round(lower_bbox[1])}_{round(lower_bbox[2])}_{round(lower_bbox[3])}"
        right_bbox_key = f"{round(bbox[0])}_{round(bbox[1])}_{round(bbox[2])}_{round(bbox[3])}"
    
        left_bbox_ID = st.session_state.bbox_details[left_bbox_key]["ID"]
        right_bbox_ID = st.session_state.bbox_details[right_bbox_key]["ID"]
        
        left_bbox_type = st.session_state.bbox_details[left_bbox_key]["type"]
        right_bbox_type = st.session_state.bbox_details[right_bbox_key]["type"]
        
        if draw:
        
            st.session_state.edges.append({"left_bbox_ID": left_bbox_ID,"right_bbox_ID": right_bbox_ID, \
                                           "left_bbox_type": left_bbox_type,"right_bbox_type": right_bbox_type ,"line": (x1,y1,x2,y2),"length": 0}) 
         
        else:
            
            return (x1,y1,x2,y2)



def get_bounding_box_by_ID(node_ID):
    
    for ind,node in st.session_state.bbox_details.items():
        if node["ID"] == node_ID:
            x = ind.split("_")
            bbox = (int(x[0]),int(x[1]),int(x[2]),int(x[3]))
            
            return bbox


node_images = {
    "ACP_BLUE": r"https://drive.google.com/file/d/1_BCkYwozUWB0LECUOADPXLVEi4-NDDU4/view?usp=drive_link",
    "ACP_RED": r"https://drive.google.com/file/d/1WM17jMT44QZN5mJ8hoG0fsEIqYXTwj17/view?usp=drive_link",
    "DSA": r"https://drive.google.com/file/d/1uDLWk1fcU7H8UDBU3d34jGsNTaV8BTqF/view?usp=drive_link",
    "BSG": r"https://drive.google.com/file/d/1Lg2yVPAuc4QSHuVipJ9x8tRwYYBJ03tt/view?usp=drive_link",
    "Target": r"https://drive.google.com/file/d/1_J710WufrDyQhrEkgb2LqiM5KYMW-_Fy/view?usp=drive_link",
    "Fire1": r"https://drive.google.com/file/d/1yLFEWRZpbj3y91fSBhBl1AJDhIIf28f3/view?usp=drive_link",
    "Fire2": r"https://drive.google.com/file/d/1eCKlfLzNwmPqveoVXQHBgfBUZ_9yhA1G/view?usp=drive_link",
    "Fire3": r"https://drive.google.com/file/d/1BL9lGuzbFSRHqEX9e9M2SRE8J8Ke2vKK/view?usp=drive_link",
    "Fire4": r"https://drive.google.com/file/d/1W-ZLqxWXROdV7hEtvZiYTnmv_fcYcYcj/view?usp=drive_link"
    
}

target_height = 100
processed_images = {}
scaling_factors = {}

for label, img_path in node_images.items():
    img,original_w, original_h, new_w, new_h = resize_image(img_path, target_height)
    processed_images[label] = img
    scaling_factors[label] = (original_w, original_h, new_w, new_h)


if "nodes" not in st.session_state:
    st.session_state.nodes = []
    
if "edges" not in st.session_state:
    st.session_state.edges = []
    
if "clicked_nodes" not in st.session_state:
    st.session_state.clicked_nodes = []
   
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None
    
if "canvas_clicked" not in st.session_state:
    st.session_state.canvas_clicked = False  
    
if "bboxes" not in st.session_state:
    st.session_state.bboxes = []
    
if "bboxes_dict" not in st.session_state:
    st.session_state.bboxes_dict = {}
    
if "bbox_details" not in st.session_state:
    st.session_state.bbox_details = {}
    
if "drawing_mode" not in st.session_state:
    st.session_state.drawing_mode = 'freedraw'
    
if "node_selected" not in st.session_state:
    st.session_state.node_selected = False
    
if "rerun" not in st.session_state:
    st.session_state.rerun = False
    
if 'object_count' not in st.session_state:
    st.session_state.object_count = 0
    
if 'previous_object_count' not in st.session_state:
    st.session_state.previous_object_count = 0
    
if 'selected_edge' not in st.session_state:
    st.session_state.selected_edge = "Select option"
    
if 'previous_selected_edge' not in st.session_state:
    st.session_state.previous_selected_edge = "Select option"
    
if 'click_behaviour' not in st.session_state:
    st.session_state.click_behaviour = "Select"
    
if 'delete_confirmation' not in st.session_state:
    st.session_state.delete_confirmation = False
    
if 'state_history' not in st.session_state:
    st.session_state.state_history = [[[],[],[],None,False,[],{}, {}, 'freedraw' , False, False, "Select option",  "Select option", "Select" , \
                                      False, None, 0, 0]]
    
if 'state_num' not in st.session_state:
    st.session_state.state_num = 0
    
if 'session_state_hist_update' not in st.session_state:
    st.session_state.session_state_hist_update = False

if 'node_index' not in st.session_state:
    st.session_state.node_index = 1

within_box = False
    
st.title("PCC5 Model Building")

canvas_background = Image.new("RGBA", (3000, 800), (255, 255, 255, 255))  
draw = ImageDraw.Draw(canvas_background)

if st.session_state.node_selected:
    draw.rectangle(st.session_state.selection_bbox, outline="red", width=2)

for node in st.session_state.nodes:
    node_img = Image.open(node_images[node["type"]]).convert("RGBA")
    node_img.thumbnail((target_height, target_height), Image.LANCZOS)   
    new_width, new_height = node_img.size
    
    original_w, original_h, _, _ = scaling_factors[node["type"]]
    bbox = node_img.getbbox()
    
    if bbox:
        
        x, y = node["pos"]
        

        bounding_box = (x + bbox[0]-2, y + bbox[1]-2, x + bbox[2], y + bbox[3])
        
        
        if bounding_box not in st.session_state.bboxes:
            st.session_state.bboxes.append(bounding_box)
            
            x1 = bounding_box[0]
            y1 = bounding_box[1]
            x2 = bounding_box[2]
            y2 = bounding_box[3]
            
            
            bbox_key = f"{round(x1)}_{round(y1)}_{round(x2)}_{round(y2)}"
            
            st.session_state.bboxes_dict[bbox_key] = "NODE" + str(st.session_state.node_index)
            st.session_state.bbox_details[bbox_key] = {"ID": "NODE" + str(st.session_state.node_index),
                                                       "type": node["type"], "Re-Order_Freq": 0, "Avg_Rate_of_Fire": 0,
                                                       "Rate_of_Fire_StDev": 0,"Damage_Avg": 0 , "Damage_StDev": 0,"Rate_of_Decay": 0, "HP": 0,
                                                       "Re-Order_Point": 0, "MSH": 0, "Re-Order_Quantity": 0, "Average_Supply_Lead_Time": 0,
                                                       "Standard_Deviation_of_Supply_Lead_Time": 0, "Safety_Stock": 0}
            
            st.session_state.node_index += 1
            
    canvas_background.paste(node_img, (x, y), node_img)
    

edge_num = 1

for edge in st.session_state.edges:
    
    if st.session_state.selected_edge == "Select option":
        draw.line(edge["line"], fill="black", width=3)
        
    elif int(st.session_state.selected_edge) == edge_num:
        draw.line(edge["line"], fill="red", width=3)
        
    else:
        
        draw.line(edge["line"], fill="black", width=3) 
    
    
    if str(edge["length"]) != "0":
        gradient = (edge["line"][3] - edge["line"][1]) / (edge["line"][2] - edge["line"][0]) 
        c = edge["line"][3] - (gradient*edge["line"][2])
        
        mid_x_point = edge["line"][0] + ((edge["line"][2] - edge["line"][0])  / 2)
        mid_y_point = mid_x_point*gradient + c - 25
        
        draw.text((mid_x_point,mid_y_point), str(edge["length"]) + "km", fill="black")
        
        
    parallel_lines = point_on_line(1,1,edge["line"])

    
    edge_num += 1
    
col1, col2 = st.columns([5, 1])

with col1:

    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)",  
        background_image=canvas_background,
        height=800,
        width=3000,#
        stroke_width=0,
        key="canvas",
    )

with col2:

    with st.expander("Set edge lengths:"):
        edges_list = list(range(1,len(st.session_state.edges)+1))
        
        selectbox_edge_num = st.selectbox("Select edge number",options=["Select option"] + edges_list,\
                                          index=(["Select option"] + edges_list).index(st.session_state.selected_edge))
        
        st.session_state.selected_edge = selectbox_edge_num
        
        if st.session_state.selected_edge != "Select option":
            
            refresh = st.session_state.selected_edge != st.session_state.previous_selected_edge
            st.session_state.previous_selected_edge = st.session_state.selected_edge

            edge_num_ind = int(st.session_state.selected_edge) - 1
            edge = st.session_state.edges[edge_num_ind]
            
            left_bbox_type = edge["left_bbox_type"]
            right_bbox_type = edge["right_bbox_type"]
            
            st.write(f"Selected edge: {left_bbox_type} to {right_bbox_type}")
            
            edge_length = st.text_input("Set edge length (km):")
            
            if st.button("Set edge length"):
                
                edge["length"] = edge_length

                st.session_state.previous_selected_edge = "Select option"
                st.session_state.selected_edge = "Select option"
                
                st.rerun()
    
            if refresh:
                st.rerun()
        
    with st.expander("Set supply vehicle speed range"):   
        low_speed = st.text_input("Enter low speed (km):")
        high_speed = st.text_input("Enter high speed (km):")
        
        if st.button("Update speed setting"):
            low_speed = float(low_speed)
            high_speed = float(high_speed)
            
            st.session_state.speed_mean_factor = (math.log(high_speed/low_speed) / (high_speed - low_speed))*60
            st.session_state.speed_var_factor = (((1/low_speed) - (1/high_speed)) / math.sqrt(12)) * 60
            
            st.write("Speed setting updated.")
        
    with st.expander("Set node parameters / delete node"):
        
        if st.session_state.node_selected:
            bbox = st.session_state.selection_bbox
            bbox_key = f"{round(bbox[0])}_{round(bbox[1])}_{round(bbox[2])}_{round(bbox[3])}"
            node = st.session_state.bbox_details[bbox_key]
            node_ID = st.empty()
            node_ID.text(f"Node ID: {node["ID"]}")
            node_type = st.empty()
            node_type.text(f"Node Type: {node["type"]}")

            if node["type"][0:4] == "Fire":
    
                avg_usage = st.text_input("Set average rounds fired / minute:", value = node["Avg_Rate_of_Fire"])
                re_order_freq = st.text_input("Set re-order frequency:", value = node["Re-Order_Freq"])

                re_order_quantity = st.empty()
                safety_stock = st.empty()
                re_order_point = st.empty()
                max_stock_level = st.empty()
                Avg_LT = st.empty()
                StdDev_LT = st.empty()

                
                re_order_quantity.text(f"Re-order quantity: {node["Re-Order_Quantity"]}")
                safety_stock.text(f"Safety Stock Level: {round(node["Safety_Stock"],2)}")
                re_order_point.text(f"Re-order point: {round(node["Re-Order_Point"],2)}")
                max_stock_level.text(f"Max stock level: {round(node["MSH"],2)}")
                Avg_LT.text(f"Avg lead time (mins): {node["Average_Supply_Lead_Time"]}")
                StdDev_LT.text(f"Std dev of lead time (mins): {node["Standard_Deviation_of_Supply_Lead_Time"]}")

      
                
            elif node["type"][0:6] == "Target":
                
                Resilience = st.text_input("Set resilience of target (HP):", value = node["HP"])

            
            else:

                re_order_freq = st.text_input("Set re-order frequency:", value = node["Re-Order_Freq"])
                re_order_quantity3 = st.empty()
                safety_stock3 = st.empty()
                re_order_point3 = st.empty()
                max_stock_level3 = st.empty()
                Avg_LT3 = st.empty()
                StdDev_LT3 = st.empty()
                re_order_quantity3.text(f"Re-order quantity: {node["Re-Order_Quantity"]}")
                safety_stock3.text(f"Safety stock level: {node["Safety_Stock"]}")
                re_order_point3.text(f"Re-order point: {node["Re-Order_Point"]}")
                max_stock_level3.text(f"Max stock level: {node["MSH"]}")       
                Avg_LT3.text(f"Avg lead time (mins) {node["Average_Supply_Lead_Time"]}")
                StdDev_LT3.text(f"Std dev of lead time (mins): {node["Standard_Deviation_of_Supply_Lead_Time"]}")
    
            if st.button("Update node attributes"):
                
                if node["type"][0:4] == "Fire":
                    node["Avg_Rate_of_Fire"] = avg_usage
                    node["Re-Order_Freq"] = re_order_freq

                elif node["type"][0:6] == "Target":
                    node["HP"] = Resilience
                
                else:
                    node["Re-Order_Freq"] = re_order_freq
            
                st.rerun()
                
            if st.button("Delete node"):
                st.session_state.delete_confirmation = True
                
            if st.session_state.delete_confirmation:
                st.warning("Are you sure you want to delete this node?")
                col1, col2 = st.columns(2)

                with col1:
                    proceed = st.button("Yes", key="proceed")
                
                with col2:
                    cancel = st.button("No", key="cancel")
            
                if proceed:
                    deleted_node_ID = st.session_state.bbox_details[bbox_key]["ID"]
                    
                    draw.rectangle(st.session_state.selection_bbox, outline="white", width=2)
                    st.session_state.selection_bbox = None
                    st.session_state.node_selected = False
                    st.session_state.bboxes.pop(st.session_state.bboxes.index(bbox))
                    del st.session_state.bbox_details[bbox_key]
                    del st.session_state.bboxes_dict[bbox_key]
                    st.session_state.nodes = [node for node in st.session_state.nodes if node["bounding_box"] != bbox]
                    st.session_state.delete_confirmation = False
                    st.session_state.edges = [edge for edge in st.session_state.edges if deleted_node_ID not in {edge["left_bbox_ID"] ,edge["right_bbox_ID"]}]
                    
                    st.rerun()
                    
                if cancel:
                    st.session_state.delete_confirmation = False
                    st.rerun()
                    
                
    with st.expander("Run inventory modelling"):
        
 
        combat_hours = st.text_input("How many hours do we expect to spend in combat per day?") 
        
        if st.button("Run inventory model"):
            
            upstream_nodes = []
            upstream_node_IDs = []
            
            for ind,node in st.session_state.bbox_details.items():
                
                node_ID = node["ID"]
                node_type = node["type"]
                supply_node_found = False
                
                if node_type[0:4] == "Fire":
                    for edge in st.session_state.edges:
                        if edge["right_bbox_ID"] == node_ID:
                            supply_distance = int(edge["length"])
                            supply_node_found = True 
                            
                            if edge["left_bbox_ID"] not in upstream_node_IDs:
                                upstream_node_IDs.append(edge["left_bbox_ID"])
                                
                            break
                            
                    if supply_node_found:
                    
                        node["Average_Supply_Lead_Time"] = round(st.session_state.speed_mean_factor*supply_distance,2)
                        node["Standard_Deviation_of_Supply_Lead_Time"] = round(st.session_state.speed_var_factor*supply_distance,2)
                        
                        st.write(f"Calculating inventory metrics for {node_ID} (a {node_type} node).")
                        
                        model_calcs = Fire_ROP_MSH_Calc(node["Avg_Rate_of_Fire"],
                                                        node["Average_Supply_Lead_Time"],node["Standard_Deviation_of_Supply_Lead_Time"],
                                                        node["Re-Order_Freq"],combat_hours)

                        node["Safety_Stock"] = model_calcs[3]
                        node["Re-Order_Point"] = model_calcs[0]
                        node["Re-Order_Quantity"] = model_calcs[1]
                        node["MSH"] = model_calcs[2]                                      
                        st.write(f"{node_ID} calcs complete.")
            
                    
            for ind,node in st.session_state.bbox_details.items():
                if node["ID"] in upstream_node_IDs:
                    upstream_nodes.append(node)
                    
            st.write(upstream_nodes)
            
            while True:
                if len(upstream_nodes) == 0:
                    break
            
                upstream_node_IDs = []
                
                for node in upstream_nodes:
                    
                    node_ID = node["ID"]
                    node_type = node["type"]
                    supply_node_found = False
                    
                    if node_type[0:4] != "Fire":
                    
                        for edge in st.session_state.edges:
                            if edge["right_bbox_ID"] == node_ID:
                                supply_distance = int(edge["length"])
                                supply_node_found = True 
                                
                                if edge["left_bbox_ID"] not in upstream_node_IDs:
                                    upstream_node_IDs.append(edge["left_bbox_ID"])
                                break            
                        
                        if supply_node_found:
                        
                            node["Average_Supply_Lead_Time"] = round(st.session_state.speed_mean_factor*supply_distance,2)
                            node["Standard_Deviation_of_Supply_Lead_Time"] = round(st.session_state.speed_var_factor*supply_distance,2)
                            
                            AvgLT = node["Average_Supply_Lead_Time"]
                            StDevLT = node["Standard_Deviation_of_Supply_Lead_Time"]
                            ROF = node["Re-Order_Freq"]
                            target_node = node
                            
                            ROF_ROQ_List = []
                            downstream_node_IDs = []
                            
                            for edge in st.session_state.edges:
                                if edge["left_bbox_ID"] == node_ID:
                                    downstream_node_ID = edge["right_bbox_ID"]
                                    
                                    if node_ID not in downstream_node_IDs:
                                        downstream_node_IDs.append(downstream_node_ID)
                                        
                            for ind,downstream_node in st.session_state.bbox_details.items():
                                if downstream_node["ID"] in downstream_node_IDs:
                                    ROF_ROQ_List.append([float(downstream_node["Re-Order_Freq"]),float(downstream_node["Re-Order_Quantity"])])
                                  
                            
                            st.write(f"Calculating inventory metrics for {node_ID} (a {node_type} node).")

                            
                            model_calcs = ROP_MSH_Calc(ROF_ROQ_List,AvgLT,StDevLT,ROF,combat_hours)
                            
                            if node["ID"] == "NODE3":
                                st.session_state.model_calcs = [ROF_ROQ_List,AvgLT,StDevLT,ROF,combat_hours]

                            node["Safety_Stock"] = model_calcs[3]
                            node["Re-Order_Point"] = model_calcs[0]
                            node["Re-Order_Quantity"] = model_calcs[1]
                            node["MSH"] = model_calcs[2]  
                            
                            st.write(f"{node_ID} calcs complete.")
                            
                        upstream_nodes = []
                        
                        for ind,upstream_node in st.session_state.bbox_details.items():
                            if upstream_node["ID"] in upstream_node_IDs:
                                upstream_nodes.append(upstream_node)
                    
        
            st.rerun()        
            
    st.session_state.click_behaviour = st.radio("Toggle click behaviour", options=["Select","Join"])

if canvas_result.json_data is not None:
    if "objects" in canvas_result.json_data:
        
        if len(canvas_result.json_data["objects"]) > 0:
            obj = canvas_result.json_data["objects"][-1]
            x, y = obj["left"],obj["top"]
            st.session_state.object_count =  len(canvas_result.json_data["objects"])
            
            if st.session_state.object_count > st.session_state.previous_object_count:
            
                edge_num = 0
                
                for edge in st.session_state.edges:
                    
                    parallel_lines = point_on_line(x,y,edge["line"])
                    
                    if parallel_lines[0]:
                        st.session_state.edges.pop(edge_num)
                        st.session_state.previous_object_count = st.session_state.object_count
                    
                        st.session_state.node_selected = False
                        st.session_state.selection_bbox = None
                        
                        if st.session_state.session_state_hist_update:
                                         
                            update_session_state()
                            st.session_state.session_state_hist_update = False 
                        
                        st.rerun()
                        
                        break


                    edge_num += 1
                    
                st.session_state.session_state_hist_update = True
                
                
    
            if st.session_state.selected_node is not None:
                
                img_path = node_images[st.session_state.selected_node]
                img, original_w, original_h, new_w, new_h = resize_image(img_path, target_height)
                
                bbox = img.getbbox()
                if bbox:
                    x = x - new_w // 2
                    y = y - new_h // 2
                    bounding_box = (x + bbox[0]-2, y + bbox[1]-2, x + bbox[2], y + bbox[3])

                    
                    overlap = False
                    
                    for bbox in st.session_state.bboxes:
                        if (bbox[2] > bounding_box[0] > bbox[0] and bbox[3] > bounding_box[1] > bbox[1]) or \
                            (bbox[2] > bounding_box[2] > bbox[0] and bbox[3] > bounding_box[3] > bbox[1]):
                            overlap = True
                
                    if not overlap:
                        st.session_state.nodes.append({"type": st.session_state.selected_node, "pos": (x, y),"bounding_box": bounding_box})
                        st.session_state.previous_object_count = len(canvas_result.json_data["objects"])
                        st.session_state.selected_node = None
                        
                        if st.session_state.session_state_hist_update:
                                         
                            update_session_state()
                            st.session_state.session_state_hist_update = False 
                        
                        st.rerun()
                
                
                st.session_state.previous_object_count = len(canvas_result.json_data["objects"])
                st.session_state.selected_node = None
            
            else:
                
                if len(canvas_result.json_data["objects"]) > 0:
                    
                    st.session_state.object_count =  len(canvas_result.json_data["objects"])
                    within_box = False
                
                    for bbox in st.session_state.bboxes:
                        
                        if (bbox[2] > x > bbox[0] and bbox[3] > y > bbox[1]):
                            
                            within_box = True 
                            
                            if st.session_state.object_count > st.session_state.previous_object_count:
                                
                                if st.session_state.node_selected and bbox == st.session_state.selection_bbox:
                                    
                                    draw.rectangle(st.session_state.selection_bbox, outline="white", width=2)
                                    st.session_state.selection_bbox = None                       
                                    st.session_state.node_selected = False
                                    st.session_state.previous_object_count = st.session_state.object_count
                                    
                                    
                                    if st.session_state.session_state_hist_update:
                                                     
                                        update_session_state()
                                        st.session_state.session_state_hist_update = False 
                                    
                                    st.rerun()
                                    break
                            
                                elif st.session_state.node_selected and st.session_state.click_behaviour == "Join" :                            
                                        draw_edge(st.session_state.selection_bbox,bbox,True)
                                        
                                        st.session_state.previous_object_count = st.session_state.object_count 
                                        draw.rectangle(st.session_state.selection_bbox, outline="white", width=2)
                                        st.session_state.selection_bbox = None
                                        
                                        st.session_state.node_selected = False
                                        
                                        if st.session_state.session_state_hist_update:
                                                         
                                            update_session_state()
                                            st.session_state.session_state_hist_update = False 
                                        
                                        st.rerun()
                                        break
                                            
                                else:
                                    
                                    if st.session_state.object_count > st.session_state.previous_object_count:
                                        
                                        if st.session_state.click_behaviour == "Select":
                                            draw.rectangle(bbox, outline="red", width=2)
                                        else:
                                            draw.rectangle(bbox, outline="blue", width=2)
                                            
                                        st.session_state.node_selected = True
                                        
                                        st.session_state.selection_bbox = bbox
                                        
                                        st.session_state.previous_object_count = st.session_state.object_count
                                        
                                        if st.session_state.session_state_hist_update:
                                                         
                                            update_session_state()
                                            st.session_state.session_state_hist_update = False 
                                            
                                        st.rerun()

                                    break
                
                if not within_box and st.session_state.node_selected:
                    
                    draw.rectangle(st.session_state.selection_bbox, outline="white", width=2)
                    
                    bbox = st.session_state.selection_bbox
                    
                    bbox_key = f"{round(bbox[0])}_{round(bbox[1])}_{round(bbox[2])}_{round(bbox[3])}"
                    node_details = st.session_state.bbox_details[bbox_key]
                    
                    node_ID = node_details["ID"]
                    
                    x, y = obj["left"],obj["top"]
                    matchFound = False
                    
                    for node in st.session_state.nodes:
                        
                        st.session_state.bounding_box = node["bounding_box"]
                        st.session_state.bbox = bbox
                        
      
                        if bbox == node["bounding_box"]:
                            img, original_w, original_h, new_w, new_h = resize_image(node_images[node["type"]], target_height)
                            x = x - new_w // 2
                            y = y - new_h // 2
                            node["pos"] = (x,y)
                            node["bounding_box"] = getBoundingBox(node_images[node["type"]],target_height,x,y)
                            

                            
                            new_bounding_box = node["bounding_box"]
                            new_bbox_key = f"{round(new_bounding_box[0])}_{round(new_bounding_box[1])}_{round(new_bounding_box[2])}_{round(new_bounding_box[3])}"
                            
                            st.session_state.bbox_details[new_bbox_key] = st.session_state.bbox_details.pop(bbox_key)
                            
                            st.session_state.bboxes.append(new_bounding_box)
                            st.session_state.bboxes.pop(st.session_state.bboxes.index(bbox))
                            
                            break
                    
                    for edge in st.session_state.edges:
                        if node_ID == edge["left_bbox_ID"]:
                            right_bbox = get_bounding_box_by_ID(edge["right_bbox_ID"])
                            
                            line = draw_edge(new_bounding_box,right_bbox,False)
                            edge["line"] = line
                            
                        elif node_ID == edge["right_bbox_ID"]:
                            

                            
                            left_bbox = get_bounding_box_by_ID(edge["left_bbox_ID"])

                            
                            line = draw_edge(left_bbox,new_bounding_box,False)
                            edge["line"] = line                            
                            
                    
                    st.session_state.selection_bbox = None
                    st.session_state.node_selected = False
                    
                    if st.session_state.session_state_hist_update:
                                     
                        update_session_state()
                        st.session_state.session_state_hist_update = False 

                    st.rerun()
    
            if st.session_state.session_state_hist_update:
                             
                update_session_state()
                st.session_state.session_state_hist_update = False 

  
st.write("### Select a Node Type")
cols = st.columns(len(node_images))

for i, (label,img) in enumerate(processed_images.items()):
    with cols[i]:
        st.image(img,width=80)
        if st.button(label):
            st.session_state.selected_node = label
            st.session_state.drawing_mode = "freedraw"


st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 20])  # Wider columns for buttons

with col1:
    if st.session_state.state_num > 0:
        if st.button("🔄 **UNDO**", key="undo_button"):
            st.session_state.state_num = max(st.session_state.state_num - 1, 0)
            state = copy.deepcopy(st.session_state.state_history[st.session_state.state_num])
            
            st.session_state.edges = json.loads(json.dumps(state[0]))
            st.session_state.nodes = json.loads(json.dumps(state[1]))
            st.session_state.clicked_nodes = json.loads(json.dumps(state[2]))
            st.session_state.selected_node = state[3]
            st.session_state.canvas_clicked = state[4]
            st.session_state.bboxes = json.loads(json.dumps(state[5]))
            st.session_state.bboxes_dict = json.loads(json.dumps(state[6]))
            st.session_state.bbox_details = json.loads(json.dumps(state[7]))
            st.session_state.drawing_mode = json.loads(json.dumps(state[8]))
            st.session_state.node_selected = json.loads(json.dumps(state[15]))
            st.session_state.rerun = json.loads(json.dumps(state[10]))
            st.session_state.selected_edge = json.loads(json.dumps(state[11]))
            st.session_state.previous_selected_edge = json.loads(json.dumps(state[12]))
            st.session_state.click_behaviour = json.loads(json.dumps(state[13]))
            st.session_state.delete_confirmation = json.loads(json.dumps(state[14]))
            st.session_state.selection_bbox = json.loads(json.dumps(state[15]))
            st.session_state.speed_mean_factor = state[16]
            st.session_state.speed_var_factor = state[17]

            st.rerun()

with col2:
    if st.session_state.state_num < (len(st.session_state.state_history) - 1):
        if st.button("🔁 **REDO**", key="redo_button"):
            st.session_state.state_num = min(st.session_state.state_num + 1, len(st.session_state.state_history) - 1)
            state = copy.deepcopy(st.session_state.state_history[st.session_state.state_num])
            
            st.session_state.edges = json.loads(json.dumps(state[0]))
            st.session_state.nodes = json.loads(json.dumps(state[1]))
            st.session_state.clicked_nodes = json.loads(json.dumps(state[2]))
            st.session_state.selected_node = state[3]
            st.session_state.canvas_clicked = state[4]
            st.session_state.bboxes = json.loads(json.dumps(state[5]))
            st.session_state.bboxes_dict = json.loads(json.dumps(state[6]))
            st.session_state.bbox_details = json.loads(json.dumps(state[7]))
            st.session_state.drawing_mode = json.loads(json.dumps(state[8]))
            st.session_state.node_selected = json.loads(json.dumps(state[9]))
            st.session_state.rerun = json.loads(json.dumps(state[10]))
            st.session_state.selected_edge = json.loads(json.dumps(state[11]))
            st.session_state.previous_selected_edge = json.loads(json.dumps(state[12]))
            st.session_state.click_behaviour = json.loads(json.dumps(state[13]))
            st.session_state.delete_confirmation = json.loads(json.dumps(state[14]))
            st.session_state.selection_bbox = json.loads(json.dumps(state[15]))
            st.session_state.speed_mean_factor = json.loads(json.dumps(state[16]))
            st.session_state.speed_var_factor = json.loads(json.dumps(state[17]))

            st.rerun()


#st.markdown(f"*Current state {str(st.session_state.state_num)}*")       
state_num = 0       
#for state in st.session_state.state_history:
    
    #st.markdown(f"*State {str(state_num)}*")
    #st.write("Selection_bbox")
    #st.write(state[15])
    #st.write("Selected node ")
    #st.write(state[3])
    #st.write("Node selected")
    #st.write(state[9])
    
    #st.write("Edges")
    #st.write(state[0])
    
    #st.write("Nodes")
    #st.write(state[1])
    
    #st.write("bbox_details")
    #st.write(state[7])
    
    #state_num += 1
