function updateContent() {
  Promise.all([
    fetch("index.html")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }
        return response.text();
      })
      .then((html) => {
        document.documentElement.innerHTML = html;
      }),
    fetch("versions.json")
      .then((res) => res.json())
      .then((data) => {
        var table = "<h2>Older versions</h2>";
        table += "<table class='table'>";
        table += "<th> versions </th>";
        table += "<th> url </th>";
        for (let versions of data) {
          table += "<tr>";
          table += "<td>" + versions.version + "</td>";
          table +=
            "<td><a href='" + versions.url + "'>" + versions.url + "</a></td>";
          table += "</tr>";
        }
        table += "</table>";
        const article = document.querySelector("article");
        const release = document.createElement("release");
        release.innerHTML = table;
        article.parentNode.replaceChild(release, article);
        const c = document.querySelector(
          "body > div.bd-container.container-xl > div > div.bd-sidebar-secondary.d-none.d-xl-block.col-xl-2.bd-toc"
        );
        c.parentNode.removeChild(c);
      }),
  ]);
}

// Call the function to update content initially
updateContent();
