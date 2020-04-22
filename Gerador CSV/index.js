const express = require('express')
const app = express()
const fs = require('fs')
const cors = require('cors')
const bodyParser = require('body-parser')
const caminho = __dirname + '/AnalisePopulacionalTratada.csv'

app.use(express.static('.'))
app.use(cors())
app.use(bodyParser.json())

function pegarCidades(results, analisePopulacional) {
    const cidades = []
    results.forEach(place => {
        let cidade = ''
        analisePopulacional.forEach(obj => {
            let lugar = place.vicinity || ''
            let result = lugar.indexOf(obj.nome) > -1
            if(result) {
                //console.log(obj.nome+` é a cidade do lugar `+lugar)
                cidade = obj.nome
            }else if(place.plus_code) {
                lugar = place.plus_code.compound_code
                result = lugar.indexOf(obj.nome) > -1
                if(result) {
                    //console.log(obj.nome+` é a cidade do lugar `+lugar)
                    cidade = obj.nome
                }
            }
        })
        cidades.push(cidade)
        /*if(place.plus_code) {
            let lugar = place.plus_code.compound_code.split('-')[0]
            if(lugar.split(',')[1]) {
                cidade = lugar.split(',')[1]
            }
        }else {
            cidade = place.vicinity
        }*/
    })
    return cidades
}



app.post('/construirCSV', (req, res) => {
    //Tratamento do arquivo
    const arquivo = fs.readFileSync(caminho, 'utf-8')
    const linhas = arquivo.split('\n')
    const analisePopulacional = linhas.map(linha => {
        dados = linha.split(',')
        return {id: dados[0], nome: dados[1]}
    }).filter(elemento => elemento.id != 'Posição' && elemento.id != '')

    //Tratar os hospitais/estados que recebi
    const {lugares, filtro} = req.body
    cidades = pegarCidades(lugares, analisePopulacional)
    novasCidades = cidades.filter(cidade => cidade.trim() != "")

    let i = 0
    const novoCSV = novasCidades.map(string => {
        let objeto = analisePopulacional.find(cidade => cidade.nome == string.trim())
        if(objeto == undefined)
            console.log('Deu ruim', string)
        return {id: i++, cidade: objeto.id, nome: objeto.nome}
    })

    let stringFinal = ''

    novoCSV.forEach(linha => {
        stringFinal += `${linha.id},${linha.cidade},\n`
    })

    fs.writeFile(__dirname + `/ocorrenciaCidades.csv`, stringFinal, err => res.status(500).send(err))
    res.status(200).send('Arquivo Salvo')
    //console.log(novoCSV)
    
    //res.send((cidades))*/
})


app.listen(3000, () => {
    console.log('Aplicação rodando')
})