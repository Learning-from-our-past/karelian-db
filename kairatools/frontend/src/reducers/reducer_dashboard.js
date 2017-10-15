export default function (state) {
  if (!state) {
    return {
      availableTools: [
        {
          key: 'csv-downloader',
          title: 'Download data',
          description: 'Download data in CSV format',
          url: '/download'
        }
      ]
    }
  }

  return state;
}
