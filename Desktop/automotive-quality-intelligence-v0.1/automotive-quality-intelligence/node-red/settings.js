module.exports = {
    flowFile: 'flows.json',
    uiPort: process.env.PORT || 1880,
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },
    editorTheme: {
        projects: { enabled: false }
    }
};
