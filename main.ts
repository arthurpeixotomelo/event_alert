// const user = 'arthur-peixoto-melo'

const data = await fetch('https://guild.host/api/next/events/upcoming').then((res) => res.json())

// const my_data = await fetch(`https://guild.host/api/next/${user}`).then((res) => res.json())

Deno.writeTextFile('./test.json', JSON.stringify(data, null, 2))