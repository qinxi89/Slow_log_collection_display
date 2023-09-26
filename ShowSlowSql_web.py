import datetime
import streamlit as st
import mysql.connector
import pandas as pd

# 连接到MySQL数据库
# pip install mysql-connector-python
db_connection = mysql.connector.connect(
    host='sh-******.com',
    port=24*9,
    user="pub****te",
    password="w*****23",
    database="slowsql_info"
)

st.set_page_config(page_title='我在AI 信息查询系统', layout='wide')
navigation = st.sidebar.radio("导航", ["慢SLQ查询", "GPU使用率"])

if navigation == "慢SLQ查询":
    # 创建游标对象
    cursor = db_connection.cursor()

    # 查询不同的表
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]

    # Streamlit应用
    st.title('数据库慢日志展示')

    current_time = datetime.datetime.now()
    st.write("当前时间 : ", current_time)

    # 数据筛选
    st.write("<br>", unsafe_allow_html=True)
    selected_table = st.selectbox('选择要查询的表', tables)
    st.info("注：仅支持查询 7 日内大于 2 秒钟的数据； 实例命名规则为 `实例 ID + _slowsql`")
    st.write("<br>", unsafe_allow_html=True)
    # 根据所选表查询数据
    if selected_table:
        query = f"SELECT * FROM {selected_table} ORDER BY update_at_time DESC"
        cursor.execute(query)
        table_data = cursor.fetchall()

        # 将查询结果转换为DataFrame
        df = pd.DataFrame(table_data, columns=[i[0] for i in cursor.description])

        # 分页功能
        page_size = 20  # 默认显示20行数据,这里有个bug，如果目标数据库数据少于20，则在下面会被判断为数据不存在
        total_pages = (len(df) + page_size -1) // page_size  # 使用 // 进行整除运算

        if total_pages > 0:
            page_number = st.selectbox("当前页数", list(range(1, total_pages + 1)), index=0)
            st.write("<br>", unsafe_allow_html=True)
            start_idx = (page_number - 1) * page_size
            end_idx = start_idx + page_size

            # 转换Time_stamp列为对应当前时间显示
            df['Time_stamp'] = pd.to_datetime(df['Time_stamp'], unit='s', utc=True)
            df['Time_stamp'] = df['Time_stamp'].dt.tz_convert('Asia/Shanghai')  # 将时区从UTC转换为您的本地时区（例如：亚洲/上海）

            # 增加表格框的宽度
            st.write("慢SQL详情(每页展示20条)： ")
            st.dataframe(df.iloc[start_idx:end_idx], width=1500, height=660)
            #st.table(df.iloc[start_idx:end_idx])

            # 使用st.markdown来靠右对齐文本
            highlighted_number = f"<span style='color:red;'>{len(df)}</span>"
            st.markdown(f'<div style="text-align: right;">共查询到 {highlighted_number} 条数据</div>', unsafe_allow_html=True)
            st.write("<br>", unsafe_allow_html=True)
            st.write("<br>", unsafe_allow_html=True)

            # 添加下载按钮以下载当前页面的数据
            st.write('下载当前页面数据：')
            csv_data = df.iloc[start_idx:end_idx].to_csv(index=False)
            st.download_button(
                label=f"下载{selected_table}_page_{page_number}.csv",
                data=csv_data.encode(),
                file_name=f'{selected_table}_page_{page_number}.csv',
                key='download-csv'
            )
        else:
            # 创建一个空的元素容器
            table_container = st.empty()
            table_container.table(pd.DataFrame())  # 显示一个空表格

        # 关闭数据库连接
        cursor.close()
        db_connection.close()

elif navigation == "GPU使用率":

    current_time = datetime.datetime.now()
    st.write("当前时间: ", current_time)


