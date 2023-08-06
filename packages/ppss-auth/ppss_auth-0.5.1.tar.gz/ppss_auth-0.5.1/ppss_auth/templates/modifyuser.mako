<%inherit file="${context['logintpl']}" />

<%
usergroups = {}
for g in user.groups:
    usergroups[g.id] = g.name
%>

<form action="${request.route_url('ppssaddcreateuser',userid=userid)}" method="POST">
    
    <input type="text" name="username" placeholder="username" value="${user.username if user else ""}">
    <br/>
    <input type="password" name="password" placeholder="password" value="">
    <br/>
    <label for="enablecheck">Enable:</label><input id="enablecheck" type="checkbox" value="1" checked="checked">
    <br/>

    <select multiple name="groups">
        %for g in allgroups:
            <option value="${g.id}" ${"selected" if g.id in usergroups else ""}>${g.name}</option>
        %endfor
    </select>
    <input type="submit" name="submit" value="Apply"/>

    <p>${msg}</p>
</form>