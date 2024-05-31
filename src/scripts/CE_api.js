let client_state = {
  sessions: [
    {
      id: 1,
      language: "c",
      source: "",
      conformanceview: false,
      compilers: [
        {
          _internalid: 1,
          id: "armv8-cclang1810",
          options: "-pthread -std=c11",
          filters: {
            binary: false,
            binaryObject: false,
            commentOnly: true,
            demangle: true,
            directives: true,
            execute: true,
            intel: true,
            labels: true,
            libraryCode: true,
            trim: false,
            debugCalls: false
          },
          libs: [],
          specialoutputs: [],
          tools: []
        }
      ],
      executors: [
        {
          compilerVisible: false,
          compilerOutputVisible: false,
          arguments: "",
          argumentsVisible: false,
          stdin: "",
          stdinVisible: false,
          compiler: {
            id: "cg141",
            options: "",
            filters: {
              binary: false,
              binaryObject: false,
              commentOnly: true,
              demangle: true,
              directives: true,
              execute: false,
              intel: true,
              labels: true,
              libraryCode: false,
              trim: false,
              debugCalls: false
            },
            libs: [],
            specialoutputs: [],
            tools: []
          },
          wrap: false
        }
      ]
    }
  ],
  trees: []
};

function processDivTags() {
  const divTags = document.querySelectorAll('div.hidden.ce');

  divTags.forEach(div => {
    const preTag = div.querySelector('pre');

    if (preTag) {
      const codeTag = preTag.querySelector('code');

      // Check if the code tag exists and get its innerHTML
      if (codeTag) {
        const code = codeTag.innerText;

        client_state.sessions[0].source = code;
        // console.log(code);

        const jsonString = JSON.stringify(client_state);
        const base64String = btoa(jsonString);
        // Replace characters in the base64 string with their Unicode representations
        const safeBase64String = base64String.replace(/[\u007F-\uFFFF]/g, (c) => {
          return '\\u' + ('0000' + c.charCodeAt(0).toString(16)).slice(-4);
        });

        const href = `https://godbolt.org/clientstate/${safeBase64String}`;

        const aTag = document.createElement('a');
        aTag.href = href;
        aTag.textContent = '▶ Open in Godbolt';

        div.insertAdjacentElement('afterend', aTag);
      }
    }
  });
}

processDivTags();
