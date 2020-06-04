const fs = require('fs')
const axios = require('axios')
const caminho = __dirname + '/AnalisePopulacionalTratada.csv'

async function ajax(estado) {
    const resultado = await axios(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${estado}/municipios`)
                /*.then(json => json)
                .catch(err => console.log(err))*/
    return resultado
}

function montarMatriz(json, cidadesFile) {
    console.log('Comecei função --------')
    const matrizFinal = []
    const cidadesJSON = json.data
    
    //filtrando
    cidadesCSV = cidadesFile.filter(cidade => cidade.nome != 'Município' && cidade.id != '' && cidade.id != 'Posição')
    //console.log('Posição', cidadesCSV)

    //primeira linha
    const primerLinha = cidadesCSV.map(cidade => cidade.id)
    primerLinha.unshift('X')
    matrizFinal.push(primerLinha)

    cidadesCSV.forEach(cidade => {
        let acharNoJSON = element => element.nome == cidade.nome
        let comparador = cidadesJSON.find(acharNoJSON)
        comparador.idCSV = cidade.id
        
        let relacao = cidadesCSV.map(cidadeCSV => {
            if(cidadeCSV.id !== comparador.idCSV) {
                cidadeCSV = cidadesJSON.find(element => element.nome == cidadeCSV.nome)
                if(cidadeCSV.microrregiao.id === comparador.microrregiao.id) {
                    return 1
                }else {
                    return 0
                }
            }else {
                return 0
            }
        })

        relacao.unshift(cidade.id)
        matrizFinal.push(relacao)
    })

    console.log('Matriz Final-------')
    let stringFinal = ''
    matrizFinal.forEach(linha => {
        linha.forEach(coluna => stringFinal += `${coluna};`)
        stringFinal += `\n`
    })
    //console.log(stringFinal)
    fs.writeFile(__dirname + '/proximidade.csv', stringFinal, err => {
        console.log(err || 'Arquivo salvo')
    })
    console.log('Fim Matriz Final ------ ')

    console.log('Terminei Função -------')
    /*console.log(cidades, cidadesCSV[0].nome)
    const obj = cidades.find(element => element.nome == cidadesCSV[0].nome)
    console.log(obj)*/
}

const conteudo = fs.readFileSync(caminho, 'utf-8')
//console.log(conteudo)
linhas = conteudo.split('\n')
ids = linhas.map(linha => {
    dados = linha.split(',')
    return {id: dados[0], nome: dados[1]}
})

ajax('33')
    .then(resultado => montarMatriz(resultado, ids))