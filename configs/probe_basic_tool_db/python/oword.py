from qtpyvcp.lib.db_tool.base import Session
from qtpyvcp.lib.db_tool.tool_table import ToolTable, Tool, ToolProperties


def tool_db(self, *args):

    # # print(f"task = {self.task}")
    
    if self.task == 1:

        tool_no = args[0]
        query = self.blocks[0].comment
        result = 0

        # # print(f"Quering {query} for tool {tool_no}")
        session = Session()
        
        table = query.split('.')[0]
        column = query.split('.')[1]
        
        if table == "tool_properties":
            tool_data = session.query(ToolProperties).filter(ToolProperties.tool_no == tool_no).first()
        
            if tool_data is not None:
                return getattr(tool_data, column, None)
            #     if column == "atc":
            #         result = tool_data.atc
            #         # print(f"ATC tool: {result}")
            #     elif column == "max_rpm":
            #         result = tool_data.max_rpm
            #         # # print(f"Max RPM: {result}")
            #     elif column == "wear_factor":
            #         result = tool_data.wear_factor
            #         # print(f"Wear factor: {result}")
            #     elif column == "bullnose_radious":
            #         result = tool_data.bullnose_radious
            #         # print(f"Bullnose radious: {result}")
            #
            #     return result
            # else:
            #    print("NO DATA")
            
        elif table == "tool":
            tool_data = session.query(Tool).filter(Tool.tool_no == tool_no).first()
        
            if tool_data is not None:
                return getattr(tool_data, column, None)
            #     if column == "remark":
            #         result = tool_data.remark
            #         # print(f"Remark: {result}")
            #     elif column == "pocket":
            #         result = tool_data.pocket
            #         # print(f"Pocket: {result}")
            #     elif column == "x_offset":
            #         result = tool_data.x_offset
            #         # print(f"x_offset: {result}")
            #     elif column == "y_offset":
            #         result = tool_data.y_offset
            #         # print(f"y_offset: {result}")
            #     elif column == "z_offset":
            #         result = tool_data.z_offset
            #         # print(f"z_offset: {result}")
            #     elif column == "a_offset":
            #         result = tool_data.a_offset
            #         # print(f"a_offset: {result}")
            #     elif column == "b_offset":
            #         result = tool_data.b_offset
            #         # print(f"b_offset: {result}")
            #     elif column == "c_offset":
            #         result = tool_data.c_offset
            #         # print(f"c_offset: {result}")
            #     elif column == "i_offset":
            #         result = tool_data.i_offset
            #         # print(f"i_offset: {result}")
            #     elif column == "j_offset":
            #         result = tool_data.j_offset
            #         # print(f"j_offset: {result}")
            #     elif column == "q_offset":
            #         result = tool_data.q_offset
            #         # print(f"q_offset: {result}")
            #     elif column == "u_offset":
            #         result = tool_data.u_offset
            #         # print(f"u_offset: {result}")
            #     elif column == "u_offset":
            #         result = tool_data.u_offset
            #         # print(f"v_offset: {result}")
            #     elif column== "w_offset":
            #         result = tool_data.w_offset
            #         # print(f"w_offset: {result}")
            #     elif column == "diameter":
            #         result = tool_data.diameter
            #         # print(f"Diameter: {result}")
            #
            #     return result
            #
            #else:
            #    print("NO DATA")
            
