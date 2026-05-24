def linear_search(head: Node, target_keyword: str) -> Node:
    current_node = head
    
    while current_node is not None:
        # Giả định thuộc tính tìm kiếm chung là 'key', trong thực tế sẽ gọi title hoặc ticket_id
        if hasattr(current_node.data, 'title') and current_node.data.title == target_keyword:
            return current_node
        elif hasattr(current_node.data, 'ticket_id') and current_node.data.ticket_id == target_keyword:
            return current_node
            
        current_node = current_node.get_next()
        
    return None