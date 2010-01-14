<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

<id>${id}</id>
<title>${title}</title>
% if description:
<subtitle>${description}</subtitle>
% endif
<updated>${updated_at}</updated>
<link href="${url}" />

% for item in items:
<entry>
    <id>urn:uuid:${item.get('id','')}</id>
    <link href="${item.get('url','')}" />
    <title>${item.get('title','')}</title>
    <updated>${item.get('updated_at','')}</updated>
    <content type="text/html">
        <div>
            % for k,v in item.get('data',{}).iteritems():
            <b>${k}</b><br>${v}<br><br>
            % endfor
        </div>
    </content>
</entry>
% endfor
</feed>
