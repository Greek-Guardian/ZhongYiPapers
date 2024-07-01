"""输入处理好的作者合著关系，建立合著网络并且划分社区，依次写入文件保存"""


import networkx as nx
from json_file_process import *
import matplotlib.pyplot as plt
import time
import numpy as np
from scipy.stats import powerlaw
import community  # python-louvain 库

province = "北京"
top_scale_communities={'year':'communities'}
storage_filename_all='%s/%sall_communities_with_all_nodes.txt'% (province, province)
storage_filename_top='%s/%stop_scale_communities_with_all_nodes.txt'% (province, province)
storage_filename_tail='%s/%stop_scale_communities_tail.txt'% (province, province)
for year in range(2010, 2023):
    start_time = time.time()
    filename = '%s/%sprocessed_author_with_id%d.json' % (province, province, year) # 输入北京processed_author_with_id2021.json
    # filename='%s/%stry%d.json' % (province, province, year)
    data=read(filename)[1:]
    # data=[
    # {
    #     "name": "张晶晶",
    #     "affiliations": ["A", "B"],
    #     "papers": ["p1", "p2", "p3"]
    # },
    # {
    #     "name": "刘岩",
    #     "affiliations": ["A", "C"],
    #     "papers": ["p1", "p3", "p4"]
    # },
    # {
    #     "name": "秋节",
    #     "affiliations": ["A", "C"],
    #     "papers": ["p4"]
    # }
    # ]

    # 创建无向图
    G = nx.Graph()

    # 添加节点和边
    for author in data:
        author_id=author['id']
        G.add_node(author_id)

        # 添加合著关系边
        for other_author in data:
            other_author_id=other_author['id']
            if author_id != other_author_id:
                common_papers = set(author["papers"]) & set(other_author["papers"])
                if common_papers:
                    G.add_edge(author_id, other_author_id, weight=len(common_papers))  # 边的权重为合作的次数

    # # 绘制带权节点图
    # pos = nx.spring_layout(G)
    # edges=G.edges()
    # # 绘制包含全部节点的网络结构图
    # weights=[G[u][v]['weight'] for u,v in edges]
    # edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}  # 构建新的权重字典列表
    # fig=plt.figure()
    # ax=plt.gca()
    # ax.set_title("Co-authorship Network with Weighted Edges %s%d"% (province, year))
    # # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)  # 带权重标签的结构图
    # # nx.draw(G, pos=pos,ax=ax,with_labels=False, node_size=1,node_color='gray', edge_color='skyblue',
    # #         width=weights,font_size=8,font_color='black')  # 边粗细随权值变化
    # # 根据度的大小筛选某些节点进行绘图
    # degrees_dict=dict(G.degree(weight='weight'))
    # selected_nodes = [node for node, degree in degrees_dict.items() if degree >= 10]  # 选择度大于等于10的节点
    # subgraph = G.subgraph(selected_nodes)
    # nx.draw(subgraph, pos=pos,node_color=[nx.eigenvector_centrality(subgraph,max_iter=200)[i] for i in subgraph.nodes],
    #         cmap=plt.cm.Blues)  # 特征向量中心性可视化
    # plt.show()
    # fig.savefig('%s/%sauthor_node%d.png' % (province, province, year))  # 保存北京author_node2010.png


    # 分析度分布
    # degrees = G.degree(weight='weight')
    # degree_sequence = [d for n, d in degrees]
    # unique_values=np.unique(degree_sequence)

    # 1直接绘制度分布直方图
    # plt.hist(x=degree_sequence, bins=unique_values, align='left',density=False,cumulative = False)
    # plt.title("Co-authorship Degree Distribution Histogram %s%d"%(province,year))
    # plt.xlabel("Degree")
    # plt.ylabel("Frequency")
    # plt.show()
    # plt.savefig('%s/%sauthor_degree真实频次%d.png' % (province, province, year)) # 保存北京author_degree2010.png

    # 2分别求对数后进行幂律分布的拟合
    # hist, bin_edges = np.histogram(degree_sequence, bins=unique_values)
    # log_data_x=np.log1p(bin_edges[:-1])
    # log_data_y=np.log(hist)
    # # 绘制散点图
    # plt.scatter(log_data_x, log_data_y)
    # # 添加标签和标题
    # plt.xlabel('Log(X)')
    # plt.ylabel('Log(Y)')
    # plt.title('Scatter Plot with Logarithmic Axes')
    # plt.show()

    partition=community.best_partition(G)
    for node,community_index in partition.items():
        G.nodes[node]['label']=community_index

    # 存为gephi格式(节点带标签）
    gephi_file_path = "%s/%scoauthorship_network%d.gexf" % (province, province, year)
    nx.write_gexf(G, gephi_file_path)


    community_stats = {}
    for node, community_index in partition.items():
        if community_index not in community_stats:
            community_stats[community_index] = [node] # 新建键值对
        else:
            community_stats[community_index].append(node)

    # 按照社区节点数量排序
    sorted_communities_top10={k:community_stats[k] for k in sorted(community_stats,key=lambda x:len(community_stats[x]),reverse=True)} # True选取大社区,False小社区
    # 得到每个社区包含的节点及其度
    top10_degree_nodes={'community_index':'nodes'}
    for community_index, stats in sorted_communities_top10.items():
        # print(f"Community {community_id} has {len(stats)} nodes: {stats}")
        community_degrees={node:G.degree(node) for node in stats}
        sorted_community_degrees={node:community_degrees[node] for node in sorted(community_degrees,key=community_degrees.get, reverse=True)} #True度从大到小,False从小到大
        top10_degree_nodes[community_index]=sorted_community_degrees
    # print(top10_degree_nodes)
    top_scale_communities[year]=top10_degree_nodes
    # todo:把标签加上去，观察划分的质量
    # for year in years:



    # # 绘制社区分布直方图
    # community_sizes = [len(stats['nodes']) for _, stats in sorted_communities]
    # plt.bar(range(len(sorted_communities)), community_sizes)
    # plt.xlabel('Community')
    # plt.ylabel('Number of Nodes')
    # plt.title('北京市Community Size Distribution')
    # plt.show()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(elapsed_time)
with open(storage_filename_all,'w') as f:
    f.write(str(top_scale_communities))#写不进去




