def selection_sort_by_revenue(head: MovieNode) -> None:
    current_node = head
    
    while current_node is not None:
        node_max = current_node
        iterator = current_node.get_next()
        
        while iterator is not None:
            if iterator.data.revenue > node_max.data.revenue:
                node_max = iterator
            iterator = iterator.get_next()
            
        if node_max is not current_node:
            current_node.data, node_max.data = node_max.data, current_node.data
            
        current_node = current_node.get_next()