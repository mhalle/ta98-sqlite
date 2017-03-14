create table f 
    (id text, 
    fma_id text, 
    fma_ancestor_id text, 
    fma_ancestor_name text, 
    hierarchy_level integer, 
    foreign key(id) references ta98(id), 
    foreign key(fma_id) references ta98(fma_id), 
    foreign key(fma_ancestor_id) references ta98(fma_id));

insert into f
    (id, fma_id, fma_ancestor_id, fma_ancestor_name, hierarchy_level)
    select fma_hierarchy.id, 
            ta98.fma_id, 
            fma_hierarchy.ancestor_id,
            fma_hierarchy.ancestor_name,
            fma_hierarchy.hierarchy_level 
        from
            fma_hierarchy join ta98 on fma_hierarchy.id == ta98.id;
    