pipeline {
  agent any

  environment {
    SIMULATE = 'true'
    CONFIRM_EXECUTE = 'false'
  }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {
    stage('Checkout') {
      steps {
        echo 'Sentinela CI — validando workspace de sustentação N1/N2'
        checkout scm
      }
    }

    stage('Backend lint & tests') {
      steps {
        dir('backend') {
          sh '''
            python3 -m venv .venv || python -m venv .venv
            . .venv/bin/activate || .venv/Scripts/activate
            pip install -r requirements.txt
            pytest -q
          '''
        }
      }
    }

    stage('Frontend build') {
      steps {
        sh '''
          npm ci || npm install
          npm run build
        '''
      }
    }

    stage('Safety gate') {
      steps {
        script {
          if (env.SIMULATE != 'true') {
            error 'Pipeline bloqueada: SIMULATE deve permanecer true fora de janela de mudança.'
          }
          echo 'Modo SIMULAR ativo — nenhuma rotina N1/N2 destrutiva será executada.'
        }
      }
    }

    stage('Package') {
      steps {
        echo 'Imagens Docker prontas para compose (api + web + jenkins).'
      }
    }

    stage('Deploy staging (simulado)') {
      steps {
        echo 'Promoção para staging registrada no audit trail. Nenhuma alteração em produção.'
      }
    }
  }

  post {
    success {
      echo 'Pipeline Sentinela concluída — artefatos aptos para demonstração.'
    }
    failure {
      echo 'Falha no pipeline. Tratar como incidente de CI e correlacionar com o último commit.'
    }
  }
}
