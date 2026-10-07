const api = (path) => new Promise((resolve, reject) => uni.request({ url: `/prod-api/english${path}`, success: ({ data }) => data && data.code === 200 ? resolve(data.data) : reject(data), fail: reject }));

export async function firstUnitWords() {
  const books = await api('/books');
  const units = books[0] ? await api(`/units?bookId=${books[0].book_id}`) : [];
  const words = units[0] ? await api(`/words?unitId=${units[0].unit_id}`) : [];
  return words.map((word) => ({ ...word, audio: Object.fromEntries(Object.entries(word.audio || {}).map(([accent, url]) => [accent, `/prod-api${url}`])) }));
}
