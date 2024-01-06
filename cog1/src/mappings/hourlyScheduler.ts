import { AnswerUpdated } from '../../generated/AccessControlledOffchainAggregator/AccessControlledOffchainAggregator'
import { updateMediumPair } from '../entities/pair'


export function onAnswerUpdated(event: AnswerUpdated): void {
    // Update priced token prices
    updateMediumPair(event.block.timestamp)
}