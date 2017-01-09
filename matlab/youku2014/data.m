%function [training, test] = data()
    connection = db();
    sql = 'SELECT a.vid,episode_num FROM (SELECT vid,MAX(nth) AS episode_num FROM youku2014.epiosde_view_mainland_chain GROUP BY vid) AS a WHERE a.episode_num>10';
    cursor = exec(connection,sql);
    setdbprefs('datareturnformat','cellarray');   %cellarray, numric, structure;
    result = fetch(cursor);
    vids = cell2mat(result.Data);   % get ids of all serials
    [m,n] = size(vids);
    views =zeros(m,max(vids(:,2)));
    for k =1:1:1
        for nth=1:1:vids(k,2)
            sql = sprintf('SELECT * FROM youku2014.epiosde_view_mainland_chain WHERE vid=%d and nth=%d ORDER BY DATE',vids(k,1),nth);
            cursor = exec(connection,sql);
            result = fetch(cursor);
            episode_views = cell2mat(result.Data);   % get views of an episode
            break;
        end
    end
    training = 0;
    test = 0;
    
%     sql = 'select * from video_profile limit 3';
%     cursor = exec(connection,sql);
%     result = fetch(cursor);
%     %setdbprefs('datareturnformat','dataset');   %cellarray, numric, structure;
%     profile = result.Data;
%     %profile = cell2mat(result.Data);
%     size(profile)
%     profile(1,:)
%     close(cursor);
%     close(connection);