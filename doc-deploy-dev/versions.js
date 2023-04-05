
(async function() {
    try {
      const [htmlResponse, jsonResponse] = await Promise.all([
      fetch("index.html"),
      fetch("versions.json")
      ]);

      if (!htmlResponse.ok) {
        throw new Error(`HTTP error: ${htmlResponse.status}`);
      }

      const html = await htmlResponse.text();
      document.documentElement.innerHTML = html;

      const versionsData = await jsonResponse.json();
      const table = createVersionsTable(versionsData);
      replaceArticleWithNewRelease(table);

      removeSidebarFromPage();
    } catch (error) {
      console.error(error);
    }
  })();

  function createVersionsTable(data) {
  let table = "<h2>Older versions</h2>";
  table += "<table class='table'>";
  table += "<thead><tr><th> # </th><th> Version </th><th> URL </th></tr></thead>";
  table += "<tbody>";
  for (let i = 0; i < data.length; i++) {
    const version = data[i];
    table += `<tr>
              <td>${i+1}</td>
              <td>${version.version}</td>
              <td><a href='${version.url}'>${version.url}</a></td>
              </tr>`;
  }
  table += "</tbody></table>";
  return table;
  }  
  function replaceArticleWithNewRelease(table) {
    const article = document.querySelector("article");
    const release = document.createElement("release");
    release.innerHTML = table;
    article.parentNode.replaceChild(release, article);
  }

  function removeSidebarFromPage() {
    const sidebar = document.querySelector(
      "body > div.bd-container.container-xl > div > div.bd-sidebar-secondary.d-none.d-xl-block.col-xl-2.bd-toc"
    );
    sidebar.parentNode.removeChild(sidebar);
  }
  