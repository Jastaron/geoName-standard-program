from Model import *
from View import *
from lib import *

class SGNS_Controller(QObject):
    view = None

    def __init__(self):
        super().__init__()

        # 创建view对象
        self.view = SGNS_View()

        # 将view的信号与自身方法连接
        self.view.standard_begin_signal.connect(self.begin_standard)
        self.view.select_file_signal.connect(self.select_file)
        self.view.output_to_csv_signal.connect(self.output_to_csv)


        # 展示
        self.show()

    # 页面展示
    def show(self):
        self.view.show()

    # 标准化
    def begin_standard(self, input_str):
        start = time()
        many_locations = input_str.split('\n')
        ans = ""
        for location in many_locations:
            ans += ",".join(output_result(location)) + "\n"
        self.view.display_result(ans)
        # print(len(many_locations),'条数据\t耗时：',time()-start,'s')

    def select_file(self):
        file_name = filedialog.askopenfilename()
        if file_name == '':
            return
        if '.csv' not in file_name and '.txt' not in file_name:
            return self.view.display_select_file_error()
        try:
            file_str = ''
            if '.csv' in file_name:
                df = pd.read_csv(file_name, header=None, dtype=str).fillna('')
            else:
                df = pd.read_table(file_name, header=None, dtype=str).fillna('')
            for i in range(len(df)):
                file_str += ','.join(list(df.iloc[i])) + '\n'
            file_str = file_str[:-1]
            self.view.display_input(file_str)
            return
        except:
            return self.view.display_select_file_error()

    def output_to_csv(self, output_str):
        file_name = filedialog.asksaveasfilename(filetypes=[('TXT','.txt'),('CSV','.csv')])
        if file_name == '':
            return
        if '.csv' not in file_name and '.txt' not in file_name:
            return self.view.display_select_file_error()
        if '.txt' in file_name:
            with open(file_name, 'w') as txt:
                txt_output_str = 'Province,City,County,PAC\n' + output_str
                txt.write(txt_output_str)
                txt.close()
            return
        output_list = output_str.split('\n')[:-1]
        for i in range(len(output_list)):
            if output_list[i] == 'nan':
                output_list[i] = [None]
                continue
            output_list[i] = output_list[i].split(',')
        output_columns = ['Province', 'City', 'County', 'PAC']
        output_df = pd.DataFrame(output_list, columns=output_columns)
        output_df.to_csv(file_name, index=False, encoding='utf-8-sig')
        return

