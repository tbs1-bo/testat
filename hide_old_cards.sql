-- hide old cards

update card
set is_visible=0
where project_name in
(
	-- project names with old milestones
	select distinct c.project_name
	from card c
	where c.id in
	(
		-- looking for cards with milestones that are older than X days
		select m.card_id
		from milestone m
		where julianday('now')-julianday(m.finished) < 500  -- X days
	)
)
